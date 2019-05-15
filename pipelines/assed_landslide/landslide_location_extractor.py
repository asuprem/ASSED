import utils.AssedMessageProcessor
import time, redis
import pdb
from sner import Ner
import nltk
import utils.helper_utils
from utils.file_utils import load_config

class landslide_location_extractor(utils.AssedMessageProcessor.AssedMessageProcessor):
    def __init__(self, debug=False):
        self.debug = debug
        self.time = time.time()
        pool = redis.ConnectionPool(host='localhost',port=6379, db=0)
        self.r=redis.Redis(connection_pool = pool)
        self.timecheck = 600
        self.locations = {}
        self.update_location_store()
        self.NER =  Ner(host="localhost", port=9199)
        self.counter = 0
        self.memory={}
        config = load_config("./config/assed_config.json")
        self.APIKEY = config["APIKEYS"]["googlemaps"]
        self.stream_tracker = {}

    def process(self,message):
        if message["streamtype"] not in self.stream_tracker:
            self.stream_tracker[message["streamtype"]] = {}
            self.stream_tracker[message["streamtype"]]["bad_location"] = 0
            self.stream_tracker[message["streamtype"]]["good_location"] = 0
            self.stream_tracker[message["streamtype"]]["totalcounter"] = 0
        if time.time() - self.time > self.timecheck:
            utils.helper_utils.std_flush("Updating news location store.")
            self.update_location_store()
            self.time = time.time()
            for _streamtype in self.stream_tracker:
                utils.helper_utils.std_flush("Processed %i elements from %s with %i good locations and %i bad locations"%(self.stream_tracker[_streamtype]["totalcounter"],_streamtype, self.stream_tracker[_streamtype]["good_location"], self.stream_tracker[_streamtype]["bad_location"]))
        if self.debug:
            utils.helper_utils.std_flush("Processed %i elements from %s with %i good locations and %i bad locations"%(self.stream_tracker[_streamtype]["totalcounter"],_streamtype, self.stream_tracker[_streamtype]["good_location"], self.stream_tracker[_streamtype]["bad_location"]))

        self.stream_tracker[message["streamtype"]]["totalcounter"] += 1
        # Check if location exists
        latitude = None
        longitude = None
        if "location" in message and message["location"] is not None and len(message["location"]) > 0:
            #already have a location
            pass
        else:
            # First location tagging to get locations...
            cleaned_message = str(message["text"].encode("utf-8"))[2:-2]
            cleaned_message = " ".join(nltk.tokenize.word_tokenize(cleaned_message))
            loc_tags = self.NER.get_entities(cleaned_message)
            desc_locations = self.extractLocations(loc_tags)
            locations = " ".join(desc_locations) if len(desc_locations) > 0 else None

            if locations is None:
                # Attempt match...
                for sublocations in self.locations:
                    if sublocations in cleaned_message:
                        locations = sublocations
                        latitude = self.locations[sublocations][0]
                        longitude = self.locations[sublocations][1]
                        break
            else:
                # This is number of location items...
                pass

                #utils.helper_utils.std_flush(self.counter)
                        
            if locations is None:
                self.stream_tracker[message["streamtype"]]["bad_location"] += 1
                return (False, message)

            # location is there, we will attempt geocoding right here... right now... right on this ship
            # With sublocations...
            if latitude is None or longitude is None:
                standardized_location = utils.helper_utils.location_standardize(locations)

                for sublocation in standardized_location.split(":"):
                    if sublocation in self.locations:
                        latitude = self.locations[sublocation][0]
                        longitude = self.locations[sublocation][1]
            
        
            message["location"] = locations
        
        # check if coords already in message
        if message["latitude"] is not None and message["longitude"] is not None:
            pass
        else:
            if latitude is not None and longitude is not None:
                message["latitude"] = str(latitude)
                message["longitude"] = str(longitude)
            else:
                # Attempt to get location from extractor memory (assed:extractor...)
                
                # First normalize...
                extractor_locations = utils.helper_utils.location_standardize(message["location"])
                # Then attempt retrieve
                coordinates = None
                for extractor_sublocation in extractor_locations.split(":"):
                    r_key = utils.helper_utils.extractor_sublocation_key(extractor_sublocation)
                    coordinates = self.r.get(r_key)
                    if coordinates is not None:
                        latlng = coordinates.decode("utf-8").split(",")
                        latitude = float(latlng[0])
                        longitude = float(latlng[1])
                        break
                
                if coordinates is None:
                    # no sublocation exists. We are gonna have to geocode
                    # TODO TODO TODO TODO -------------
                    utils.helper_utils.std_flush("Performing geolocation for %s using googlemaps"%message["location"])
                    latitude,longitude = utils.helper_utils.lookup_address_only(message["location"], self.APIKEY, self.r)
                    if latitude == False:
                        raise RuntimeError("Maps API Expired for %s"%time.time())
                    #self.counter+=1
                    #utils.helper_utils.std_flush(message["location"], self.counter)
                    if latitude is not None and longitude is not None:
                        coordinates = str(latitude) + "," + str(longitude)
                        for extractor_sublocation in extractor_locations.split(":"):
                            r_key = utils.helper_utils.extractor_sublocation_key(extractor_sublocation)
                            # TODO ADD TO MEMORY AS WELL
                            self.r.set(r_key, coordinates, ex=259200)
                    
            if latitude is not None and longitude is not None:
                message["latitude"] = str(latitude)
                message["longitude"] = str(longitude)
            else:
                self.stream_tracker[message["streamtype"]]["bad_location"] += 1
                return (False, message)
        self.stream_tracker[message["streamtype"]]["good_location"] += 1
        return (True, message)
        


    def update_location_store(self,):
        self.locations = {}
        for _key in self.r.scan_iter(match="assed:sublocation:*", count=500):
            # keep only the first key location
            key_location = _key.decode("utf-8").split("assed:sublocation:")[1]
            if key_location.strip():
                key_coords = self.r.get(_key).decode("utf-8").split(",")
                latitude = float(key_coords[0])
                longitude = float(key_coords[1])
                self.locations[key_location] = (latitude, longitude)


    def extractLocations(self,temp_loc_tags):
        locations = []
        temp_loc=[]
        if temp_loc_tags[0][1] == 'LOCATION':
            temp_loc.append(temp_loc_tags[0][0])
        for entry in temp_loc_tags[1:]:
            if entry[1] == 'LOCATION':
                temp_loc.append(entry[0])
            else:
                if temp_loc:
                    locations.append(' '.join(temp_loc))
                    temp_loc=[]
        if temp_loc:
            locations.append(' '.join(temp_loc))
        return locations