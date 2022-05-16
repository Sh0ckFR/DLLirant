# DLLirant
DLLirant is a tool to automatize the DLL Hijacking researches on a specified binary.

![alt text](https://raw.githubusercontent.com/Sh0ckFR/DLLirant/main/screenshot.png)

## Live Demo

![alt text](https://raw.githubusercontent.com/Sh0ckFR/DLLirant/main/live.gif)

## How to install

You need to install Visual Studio Community Edition or superior.

Start `DLLirantDLL.sln` in the directory "DLLirantDLL" to update the Visual Studio version on the project and select "Release x64" in the Visual Studio top menu and close Visual Studio (just one time).

Install pefile from pip:

```
pip3 install pefile
```

## How to use

In a first time you need to start a command line with the tool `x64 Native Tools Command Prompt for VS` (search with the windows touch)

Use the `cd` command to your DLLirant directory and to test a binary:

```
python3 DLLirant.py -f "C:\THEFULLPATH\YourBinary.exe"
```

If you want to create a proxy dll, you can use the -p option on the original vulnerable dll (read https://itm4n.github.io/dll-proxying/ for more informations):

```
python3 DLLirant.py -p "C:\THEFULLPATH\VulnerableDLL.dll"
```

## How it works

The script will create an output directory in the same directory of DLLirant.py, copy the targeted binary to the output directory.

Via the pefile library, the script will extract the dll names required by the binary, and test each imports functions available one by one by compilate a custom DLL with the required exported functions.

If a function required by the binary is executed, the custom DLL will create a `C:\\DLLirant\\output.txt` file and display a MessageBox to be sure that a DLL Hijacking is possible.

A `results.txt` will be also created in the DLLirant directory with all potential DLL Hijacking available.

A file `admin-required.txt` will also be available for the potential DLL Hijacking who require specific privileges.

If a binary require a DLL from the system or another one, you can create a `import` directory in the same directory of `DLLirant.py` the script will copy all your DLL files in the `output` directory with your targeted binary.

## Technical posts (in French)

* https://sh0ckfr.com/pages/martine-a-la-recherche-de-la-dll-hijacking-perdue/
* https://sh0ckfr.com/pages/martin-et-le-dll-proxying-de-cristal/

## Credits

* [am0nsec](https://twitter.com/am0nsec)
* DallasFR
* Justin Bui from SpecterOps for his blogpost and the idea: https://posts.specterops.io/automating-dll-hijack-discovery-81c4295904b0
* itm4n for his blogpost about DLL Proxying: https://itm4n.github.io/dll-proxying/
* [bik3te](https://twitter.com/bik3te)
* The authors of the pefile library: https://github.com/erocarrera/pefile
