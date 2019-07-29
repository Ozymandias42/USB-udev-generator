import subprocess
import pprint
import os

arr=()
USB_DEVICES_CMD='lsusb|sort -t" " -k 7|awk \'!/[h,H]ub/ {print $0}\''

def getShellCmdOut(cmd, useshell):
	process=subprocess.run(cmd, universal_newlines=True,shell=useshell, stdout=subprocess.PIPE)
	out=process.stdout[0:-1].split('\n')
	return list(out)

def selectFromKdialog(text,list2selectFrom):
    cmd=["kdialog", "--menu", str(text)] 
    cmd.extend([str(x) for a in enumerate(list2selectFrom) for x in a])
    return getShellCmdOut(cmd, False)

def selectFromZenity(text, list2selectFrom):
    cmd=["zenity", "--list", str(text), "--column", "Device name"]
    cmd.extend(list2selectFrom)
    return getShellCmdOut(cmd, False)

def selectFromTerminal(text, list2selectFrom):
    print(text)
    for i,x in enumerate(list2selectFrom):
	    print(f"({i}) {x}")
    return input("Your choice:")

def getUSBdevDict(arr):
    arr=map(lambda x: x.split(' ', 6), arr)
    usbDictArr=[]
    for i in arr:
	    IDs=i[5].split(':')
	    usbDictArr.append({"Bus":i[1], "Device":i[3][0:-1], "VendorID": IDs[0], "DeviceID":IDs[1], "Name":i[6]})
    return usbDictArr

windowText="Select USB device you want to use to resume your computer"
arr=getShellCmdOut(USB_DEVICES_CMD, True)
usbDictArr=getUSBdevDict(arr)

#pprint.PrettyPrinter(indent=4).pprint(usbDictArr)

if(os.environ['XDG_CURRENT_DESKTOP'] == "KDE"):
    if(getShellCmdOut(["which", "kdialog"], False) != "kdialog not found"):
	    selection=selectFromKdialog(windowText, [x["Name"] for x in usbDictArr])
	    selection=int(selection[0])
    else:
	    selection=selectFromTerminal(windowText, [x["Name"] for x in usbDictArr])
	    selection=int(selection)
else: 
    if(getShellCmdOut(["which", "zenity"], False) != "zenity not found"):
	    selection=selectFromZenity(windowText, [x["Name"] for x in usbDictArr])
    else:
	    selection=selectFromTerminal(windowText, [x["Name"] for x in usbDictArr])
	    selection=int(selection)


syspath=getShellCmdOut(["udevadm", "info", "--query", "path", "/dev/bus/usb/"+usbDictArr[selection]['Bus']+"/"+usbDictArr[selection]['Device']], False)
print(syspath)

udevrule='SUBSYSTEM=="usb", '+\
	'ATTRS{idVendor}=="'+usbDictArr[selection]["VendorID"]+'", '+\
	'ATTRS{idProduct}=="'+usbDictArr[selection]["DeviceID"]+'", '+\
	'RUN+=\'echo "enabled" > /sys/$env{DEVPATH}/power/wakeup\''

print(udevrule)
#print("Requiring sudo password for next step.")
#paswd=input("Please enter:")
#proc=subprocess.Popen(f"echo '{udevrule}' |sudo tee /etc/udev/rules.d/96-usb-wakeup.rules",universal_newlines=True, shell=True, stdin=subprocess.PIPE)
#proc.communicate(passwd)
