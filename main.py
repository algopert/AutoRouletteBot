import Autobet 
import keyboard
import sys
from my_license import License

def quit():
    sys.exit()
    
if __name__ == "__main__":

    try:
        _license = License()
        dev_key = _license.generate_device_uuid_hash()
        with open('./License/device.key', 'w') as f:
            f.write(dev_key)
        print(dev_key)
    except:
        print("It doesn't exist license folder!!!, please create the folder named with 'license'")
        print("\nQ: press to continue...")
        while True:
            if keyboard.is_pressed("q"):
                break
        quit()

    try:
        with open('./License/license.key', 'r') as f:
            lic_key = f.read()
            print('lic key = ', lic_key)
    except:
        print("It doesn't exist license file!, please buy the license key!!")
        print("\nQ: press to continue...")
        while True:
            if keyboard.is_pressed("q"):
                break
        quit()
    
    
    
    _autobet = Autobet.AutoBet()
    _autobet.startProcess()