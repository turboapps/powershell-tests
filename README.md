# Turbo.net Image Test

This repository contains test scripts designed for testing images (applications) built using our scripts from the powershell-builds repository: https://github.com/turboapps/powershell-builds. The scripts aim to verify the functionality and performance of these applications. The focus is on essential operations such as application launch, basic functions, file handling, and user assistance features.

The repository also contains an HTA tool that makes it easy to run indivdual tests for the images pulled from either the Turbo.net Hub or from your own Turbo Hub server.  The HTA tool also provides the option of pushing a successfully tested image to another Turbo Hub server.

## Prepare the test environment:

1. It is recommended to use a clean virtual machine for the tests. The test environment should not have the applications being tested installed locally.

2. Windows 10 and 1080p resolution (1920 X 1080): the tests are dependent on the SikuliX GUI test. SikuliX scripts utilize image recognition and may fail if the operating system or resolution doesn't meet these requirements.  

3. Download this repository or use the `git clone` command.

4. Install Turbo Client: download and install the latest Turbo Client from https://turbo.net/download#client.

## Run the tests:

1. Launch the `TurboImageTester.hta`.

2. Input your Turbo Server URL and API key (no API key needed if using Turbo.net Hub). The test script will pull the supporting images from Turbo.net Hub and the images to be tested from your Turbo Server. This information will be saved to `.\Scripts\Common\secrets.txt`.

3. Choose an image that you wish to test from the dropdown box.

4. If you select an image that requires additional information, like login credentials, a "Required vendor info" panel will appear where you can provide these details. The information will be saved to `.\Scripts\<image>\resources\secrets.txt`.  For example, many of the Adobe applications require that you supply credentials for an Adobe account that has a valid license to launch the application.

5. Publish (optional): check the "Publish After Test" box if you want the image to be published to a Turbo Server after a successful test. You will need to fill in the Server URL and API Key for the Turbo server you are pushing the image to as well as the Version you wish the package to be pushed as.  At the end of a successful test you will get a dialog confirming that you want to publish the image.

6. Test: click the "Test Image" button to run the test. It is advised to close all other windows before running a test.

7. Logs: the test log files are saved to `%userprofile%\Desktop\Log`.

## Test folder structure

The tests are created using [SikuliX](http://sikulix.com/), a GUI-based automation tool. The test scripts are drafted in Python syntax. For more information, check [SikuliX Documentation](https://sikulix-2014.readthedocs.io/en/latest/index.html). The scripts for `7-zip_7-zip` and `adobe_acrobatpro` are well-documented, serving as a useful example for understanding the script structure.

```
.
└── Scripts/
    ├── Common/
    │   └── ...
    ├── 7-zip_7-zip/
    │   ├── Executor.ps1
    │   └── test.sikuli/
    │       ├── test.py
    │       └── ...
    ├── adobe_acrobatpro/
    │   ├── Executor.ps1
    │   ├── test.sikuli/
    │   │   ├── test.py
    │   │   └── ...
    │   └── resources/
    │       ├── secrets.txt
    │       └── ...
    └── ...
```

The `Common` folder contains common code and shared resources utilized by all test scripts. Within each image test's folder, `Executor.ps1` is a PowerShell script that controls the test. It can be run standalone for debugging purpose. Inside `test.sikuli` folder there's a `test.py`: this is the test script. In certain image tests, you may also find `resources` folders.

## Build your own tests or modify ours

1. Pull the required images from the Turbo.net Hub:

```
turbo config --domain=turbo.net
turbo run sikulix/sikulixide,oracle/jre-x64 --isolate=merge
```

2. In the SikulixIDE File > Open > Browse to the "test.py" test script for the application you wish to modify