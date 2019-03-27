import json, os, sys
import multiprocessing
from utils.helper_utils import readable_time
from datetime import datetime, timedelta
import time

'''
StreamKeyProcessor, given a list of keywords, sorts files into its given folder path
    start_time  - the start-time for this Processor. This is used in case of crashes. Parent tracks start-time for each pair
                - This is a datetime object
                - StreamKeyProcessor can do the following for time processing
                    - check which file has been created in output directory. Get the next one from input directory (minute lossy)
                    - check most recent timestamp of output file, and continue from there (more granular)
                    - for each timestamp processed, register with parent. When start, parent informs about timestamp
    keywords    - a list of keywords for this StreamKeyProcessor
    root_name   - the name_lang pair for this processor, ex: "landslide_en"
'''
class StreamFilesProcessor(multiprocessing.Process):
    def __init__(self, startTime, keywords, rootName, errorQueue,messageQueue, SOCIAL_STREAMER_FILE_CHECK_COUNT):
        multiprocessing.Process.__init__(self)

        ''' Set up the time counter 
            Note the finishedUpToTime MUST be a datetime object '''
        if startTime is None:
            self.fishedUpToTime = time.time()
        else:
            self.fishedUpToTime = startTime
        #reset seconds to 0
        self.finishedUpToTime -= timedelta(seconds=self.finishedUpToTime.second)
        self.timeDelta = timedelta(seconds=60)

        ''' Message queue for passing back errors and current times '''
        self.errorQueue = errorQueue
        self.messageQueue = messageQueue

        ''' set up relevant details '''
        self.keywords = keywords
        self.rootName = rootName
        self.DOWNLOAD_PREPEND = './downloads/'
        self.SOCIAL_STREAMER_FILE_CHECK_COUNT = SOCIAL_STREAMER_FILE_CHECK_COUNT

    def run(self):
        ''' Starts the Processor '''
        try:
            #Run forever
            while True:
                #If we are not two minutes behind, we have to wait (to make sure the file is finished being written to)
                if (datetime.now() - self.finishedUpToTime).seconds < 120:
                
                    waitTime = 120 -  (datetime.now() - self.finishedUpToTime).seconds
                    time.sleep(waitTime)
                else:
                    #We are not two minutes behind. We can start attempting to see if the file exists
                    
                    filePath = self.getInputPath()

                    if not os.path.exists(filePath):
                        # At this point, we are at least 2 minutes behind, but the file still has not been created. So we wait for four total minutes
                        waitTime = (datetime.now()-self.finishedUpToTime.second).seconds
                        #Difference is less than Four minutes
                        if waitTime < 60 * (self.SOCIAL_STREAMER_FILE_CHECK_COUNT + 1):
                            waitTime = waitTime - (60 * (self.SOCIAL_STREAMER_FILE_CHECK_COUNT + 1))
                            time.sleep(waitTime)
                        else:
                            #difference is more than four minutes - we can increment the the by one minute for the next ones
                            self.updateTime()
                    else:
                        #So at this point, we have a file and its been at least two minutes
                        
                        #Open the output writing path
                        outputPath = self.getOutputPath()
                        outputWritePath = open(outputPath, 'a')
                        with open(filePath, 'r') as fileRead:
                            
                            for line in fileRead:
                                #try to read the file if it fails skip it
                                try:
                                    jsonVersion = json.loads(line.strip())
                                    #Now we check if our keywords match
                                    for keyword in self.keywords:
                                        if keyword in jsonVersion:
                                            #write this to file
                                            outputWritePath.write(line)
                                            continue
                                    #So the previous one did not match the keyword
                                    #Now we go to the next line
                                except:
                                    #Maybe some error
                                    pass
                        #Done with file. Increment counter
                        outputWritePath.close()
                        self.updateTime()


        except Exception as e:
            self.errorQueue.put((str(e)))



    def updateTime(self):
        self.finishedUpToTime += self.timeDelta

    def getInputPath(self):
        pathDir = os.path.join(self.PREPEND + '%s_%s_%s' % ('tweets', 'unstructured', self.finishedUpToTime.year), '%02d' % self.finishedUpToTime.month,
                                        '%02d' % self.finishedUpToTime.day, '%02d' % self.finishedUpToTime.hour)
        filePath = os.path.join(pathDir, '%02d.json' % self.finishedUpToTime.minute)
        return filePath

    def getOutputPath(self):
        pathDir = os.path.join(self.PREPEND + '%s_%s_%s' % ('tweets', self.rootName, self.finishedUpToTime.year), '%02d' % self.finishedUpToTime.month,
                                        '%02d' % self.finishedUpToTime.day, '%02d' % self.finishedUpToTime.hour)
        filePath = os.path.join(pathDir, '%02d.json' % self.finishedUpToTime.minute)
        return filePath




