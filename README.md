# Pretendo-Account-Generator

Small Tool that can create a valid account.dat file to use with Cemu

![](https://i.imgur.com/ECskrmX.png)

## Usage:

First off you need an Pretendo Account, you can create one [here](https://pretendo.network/account/register)

- Download the latest release from [here](https://github.com/TheCraZyDuDee/Pretendo-Account-Generator/releases/latest/download/Pretendo.Account.Generator.exe)
- Run the Tool and Enter all the Information nessesary and press the "Generate Account" Button
- merge the mlc01 folder with your existing one

Please only use those Accounts with Cemu since you can easily create them on a real Wii U and you don't want to risk bricking your system<br>

## Building:

Currently Windows only (had some issues with running the script on Linux)!

- Download the Repository via git or just as zip
- Install [Python](https://www.python.org/downloads/) and add it to System Path'
- Install PyInstaller using `pip install pyinstaller`
- cd to the directory containing the .ico, .py and .spec file and run `pip install -r requirements.txt` and then `pyinstaller account-gen-gui.spec` or just run the build.bat

## FaQ:

Q: Why did you make this if you need a real Console anyway?<br>
A: Pretty much because it's simpler and faster to create an Account quickly here instead of on a Wii U when you ever need another Account for some reason.

Q: Why does this require my password and will my personal information be saved somewhere?<br>
A: The Password is only required to create a PasswordHash for the account.dat. This Tool does not save any input from the user the only thing that leaves your system is your PNID which we need for the PNIDLT API to fetch other required data from your Pretendo account.

Q: Can i use this to evade a ban?<br>
A: No you can't! Your Console gets banned aka. your otp.bin which will not be usable for Pretendo anymore.

Q: Will you provide the other files needed for going online?<br>
A: Absolutely not! Sharing your Online files is a pretty dumb thing to do anyway since they are unique to your console, if you wanna play on Pretendo you have to buy a Wii U.

Q: Can't i just use the Fake Online Files from [here](https://github.com/SmmServer/FakeOnlineFiles)?<br>
A: In the early days you actually could but not anymore to preventing Cheating.

## Special Thanks to:

- [Pretendo Team](https://pretendo.network) for their amazing work on the replacement Nintendo Servers
- [GabIsAwesome](https://github.com/GabIsAwesome) for his [Generator](https://github.com/GabIsAwesome/accountfile-generator) to generate the PasswordHash, MiiName, MiiData and PID and for [PNIDLT](https://pnidlt.gabis.online/) to fetch the Accounts Mii name, MiiData and PID without all this i couldn't have possibly made this Tool
- [WiiBrew](https://wiibrew.org) for their Country Code list found [here](https://wiibrew.org/wiki/Country_Codes)
- [CustomTkinter](https://customtkinter.tomschimansky.com/)
- [Akascape](https://github.com/Akascape) - [CTkScrollableDropdown](https://github.com/Akascape/CTkScrollableDropdown), [CTkMessagebox](https://github.com/Akascape/CTkMessagebox)
