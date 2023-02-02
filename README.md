# Lokatza sweepstake reader

Digitalization of the Lokatza sweepstake papers reading.

## How to use

### Set your working environment

1. Install [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam&gl=US) in your phone
2. Set the phone in an estable position on top of a blank surface
3. Set some markers in the surface to know where to put the papers

### Start the server

1. Download the project code
2. Create a python virtual environment: `virtualenv virt`
3. Activate the virtual environment: `source virt/bin/activate`

### Start reading the papers

The system needs a "baseline" in order to to know the numbers of each cell. In order to "learn" it.

For that:

1. The system needs a "baseline" in order to to know the numbers of each cell. In order to "learn" it, run: `python3 main/lokatza.py -u #webcam_url --cyclists-number 176 -l`
2. Now put an non-filled sweepstake paper in the markers, and once all the cells are highlighted in green, click `esc`. This will take a while. Have a look on the logs to see if the numbers are being processed properly

Once this is done, the real work can begin. The program continues already reading, but if you need to restart the app, you can skip the learning stage simply not passing the `-l` flag. 

To read the filled papers:

1. Put the paper in the markers
2. Once all the cells are highligthed in green, click `esc`
3. The app starts finding the marks
4. When the 15 marks are highlighted, click `esc`
5. Repeat

## Known limitations

The marked cells finding algorithm works in a best-effort approach, and at some times it is not able to find the 15 marks, if the cells are not properly filled.
To have the best results, the cells must be completely written by a pen or highligther (in this 2nd scenario, the finding takes longer)


