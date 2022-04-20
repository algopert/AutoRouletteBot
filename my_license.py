from datetime import date, datetime
import hashlib
import uuid
from urllib.request import urlopen




class License:
    def getOnlineUTCTime(self):
        internettime = urlopen("http://just-the-time.appspot.com/").read()
        OnlineUTCTime = datetime.strptime(internettime.decode('ascii').strip(), '%Y-%m-%d %H:%M:%S').date()
        return OnlineUTCTime
    def my_hash(self, str):
        hex_dig = hashlib.sha256(str.encode('ascii')).hexdigest()
        return hex_dig
        
    def generate_device_uuid_hash(self):
        return self.my_hash("Good Luck" + str(uuid.UUID(int=uuid.getnode())) + "Lets make money")
        

    def generate_exiration_key(self, uuid_hash_key, yy, mm, dd):
        return self.my_hash("For my son " + uuid_hash_key + 'Key: {0:04}-{1:02}-{2:02}'.format(yy, mm, dd))
        

    def find_expiration_day(self, date_hash_key):
        for yy in range(5):
            for mm in range(12):
                for dd in range(31):
                    if self.generate_exiration_key(self.generate_device_uuid_hash(), yy+2022, mm+1, dd+1) == date_hash_key:
                        # print('Expiration day:', yy+2022, mm+1, dd+1)
                        return date(yy+2022, mm+1, dd+1)
        print('Please buy the expiration key!')
        quit()


