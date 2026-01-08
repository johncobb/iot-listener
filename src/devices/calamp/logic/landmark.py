
FTTODECIMALDEGREES = (6076.1093456638*60)

class Landmark:
    def __init__(self, trigger_proximity, trigger_park_required, landmark_latitude, landmark_longitude):
        self._trigger_proximity = trigger_proximity/FTTODECIMALDEGREES
        self._trigger_park_required = trigger_park_required
        self._landmark_latitude = float(landmark_latitude)
        self._landmark_longitude = float(landmark_longitude)

    def calc(self, device_loc):
        (device_latitude, device_longitude) = device_loc
        dlat = device_latitude-self._landmark.latitude
        dlon = device_longitude-self._landmark.longitude
        radix = dlat*dlat + dlon*dlon <= self._landmark.trigger_proximity*self._landmark.trigger_proximity
        # self._client_log.debug1("landmark: {}({}<={})".format(radix, dlat*dlat + dlon*dlon, self._landmark.trigger_proximity*self._landmark.trigger_proximity))
        return radix

    @property
    def trigger_proximity(self):
        return self._trigger_proximity
    @property
    def trigger_park_required(self):
        return self._trigger_park_required
    @property
    def latitude(self):
        return self._landmark_latitude
    @property
    def longitude(self):
        return self._landmark_longitude
    @property
    def loc(self):
        return (self._landmark_latitude, self._landmark_longitude)

class LandmarkStore:
    def __init__(self, landmarks):
        self._account_store = {}

        # Take the landmarks dictionary object from the database.
        for landmark in landmarks:
            print(landmark)
            if self._account_store[landmark['AccountId']] == None:
                self._account_store[landmark['AccountId']] = {}
            self._account_store[landmark['AccountId']][landmark['RecordId']] = Landmark(landmark['TriggerProximity'], landmark['TriggerParkRequired'], float(landmark['Latitude']), float(landmark['Longitude']))

    def change_landmark_store(self, account_id, landmark_id, new_landmark):
        """
        Takes an account and landmark ids to update the landmark in the store
        """
        # check if the landmark exists
        if self._account_store[account_id][landmark_id] == None:
            return

        # replace landmark
        self._account_store[account_id][landmark_id] = new_landmark

        # prune old cache'd valid locations Do this in clients cache
        # self._prune_cache(account_id, landmark_id)

    def _check_store_exists(self, account_id, landmark_id):
        try:
            self._store_cache[account_id][landmark_id]
            return (account_id, landmark_id)
        except:
            try:
                self._store_cache[account_id]
                if landmark_id == None:
                    return (account_id, self._account_store[account_id])
                return (account_id, None)
            except:
                return (None, None)

    def _check_store(self, loc, account_id, landmark_id):
        try:
            if self._account_store[account_id][landmark_id].calc(loc):
                return (account_id, landmark_id)
        except:
            pass

        if account_id == None and landmark_id == None:
            for account_id in self._account_store:
                landmark_ids = ()
                for landmark_id in self._account_store[account_id]:
                    if self._account_store[account_id][landmark_id].calc(loc):
                        landmark_ids += (landmark_id, )
                    else:
                        continue
                return (account_id, landmark_ids)

        if landmark_id == None:
            landmark_ids = ()
            for landmark_id in self._account_store[account_id]:
                if self._account_store[account_id][landmark_id].calc(loc):
                    landmark_ids += (landmark_id, )
                else:
                    continue
            return (account_id, landmark_ids)

        return None

    def check(self):
            # check if account_id or landmark_id exists in store
        possible_info = self._check_store_exists(account_id, landmark_id)

        # if exists in store -> see if loc is inside a landmark
        if possible_info != (None, None):
            (_account_id, _landmark_ids) = possible_info
            for _landmark_id in _landmark_ids:
                if self._check_store(loc, _account_id, _landmark_ids):
                    self._insert_cache(_account_id, _landmark_id, loc)
                    return (_account_id, _landmark_id)



class LandmarkStack:
    def __init__(self):
        self._stack = []

    def push(self, landmark_id):
        self._stack.append(landmark_id)

    def pop(self):
        return self._stack.pop()


class LandmarksProcessor:
    """
    cache looks like
    {<account_id> : [ (lat, long), ..., (valid lat long)]}
    """
    def __init__(self, log):
        self._log = log
        self._store = None

    def load_landmarks(self, landmarks):
        if self._store != None:
            return

        self._store = LandmarkStore(landmarks)

    def is_landmark(self, account_id, device_loc):
        # return self._cache.check(device_loc, account_id)
        return self._store.check(device_loc, account_id)

    @property
    def landmarks_loaded(self):
        return self._store != None



class LandmarkCache:
    def __init__(self):
        # updated as device locs are validated
        self._account_cache = {}

        # updated from database landmarks table
        self._account_store = None

    def load_landmark_store(self, landmarks):
        """
        Take the landmarks dictionary object from the database.
        @landmarks - dict - The database object
        """




    def _insert_cache(self, account_id, landmark_id, loc):
        if self._account_cache[account_id] == None:
            self._account_cache[account_id] = {}

        # check if landmark is in account cache
        if (self._account_cache[account_id][landmark_id] == None):
            self._account_cache[account_id][landmark_id] = ()

        # add the valid device loc to cache'd tuple
        self._account_cache[account_id][landmark_id] += (loc,)

    def _prune_cache(self, account_id=None, landmark_id=None):
        if account_id == None:
            self._account_cache = {}
            return

        if landmark_id == None:
            self._account_cache[account_id] = {}
            return

        self._account_cache[account_id][landmark_id] = ()

    def _check_cache_exists(self, account_id, landmark_id):
        try:
            self._account_cache[account_id][landmark_id]
            return (account_id, (landmark_id, ))
        except:
            try:
                self._account_cache[account_id]
                if landmark_id == None:
                    return (account_id, self._account_cache[account_id])
                return (account_id, None)
            except:
                return (None, None)



    def _check_cache(self, loc, account_id, landmark_id):
        for landmark in self._account_cache[account_id][landmark_id]:
            if landmark == loc:
                return True
            else:
                continue


    def check(self, loc, account_id=None, landmark_id=None):

        # check if account_id and or landmark_id exists in cache
        possible_info = self._check_cache_exists(account_id, landmark_id)

        # if exist in cache -> see if loc in cache
        if possible_info != (None, None):
            (_account_id, _landmark_ids) = possible_info
            for _landmark_id in _landmark_ids:
                if self._check_cache(loc, _account_id, _landmark_id):
                    return (_account_id, _landmark_id)



        return None


    @property
    def landmark_cache_loaded(self):
        return self._landmark_cache != None

