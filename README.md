# Pretendo-Account-Generator

Small Tool that can create a valid account.dat file to use with Cemu

![](https://i.imgur.com/ORqWrc1.png)

### Usage

First off you need an Pretendo Account, you can create one [here](https://pretendo.network/account/register)

- Download the latest release from [here](https://github.com/TheCraZyDuDee/Pretendo-Account-Generator/releases/latest/download/Pretendo.Account.Generator.exe)
- Run the Tool and Enter all the Information nessesary and press the "Generate Account" Button
- merge the mlc01 folder with your existing one

Note that you will still need the rest of the Online Files from a Console Fake Files won't work.<br>
Please only use those Accounts with Cemu since you can easily create them on a real Wii U and you don't want to risk bricking your system<br>

### Building

Currently Windows only!

- Download the Repository via git or just as zip
- Install [Python](https://www.python.org/downloads/) and add it to System Path'
- Install PyInstaller using `pip install pyinstaller`
- cd to the directory containing the .ico, .py and .spec file and run `pip install -r requirements.txt` and then `pyinstaller account-gen-gui.spec` or just run the build.bat


### Special Thanks to:

- [Pretendo Team](https://pretendo.network) for their amazing work on the replacement Nintendo Servers
- [GabIsAwesome](https://github.com/GabIsAwesome) for his [Generator](https://github.com/GabIsAwesome/accountfile-generator) to generate the PasswordHash, MiiName, MiiData and PID and for [PNIDLT](https://pnidlt.gabis.online/) to fetch the Accounts Mii name, MiiData and PID without all this i couldn't have possibly made this Tool
- [WiiBrew](https://wiibrew.org) for their Country Code list found [here](https://wiibrew.org/wiki/Country_Codes)
- [CustomTkinter](https://customtkinter.tomschimansky.com/)
- [Akascape](https://github.com/Akascape) - [CTkScrollableDropdown](https://github.com/Akascape/CTkScrollableDropdown), [CTkMessagebox](https://github.com/Akascape/CTkMessagebox)
