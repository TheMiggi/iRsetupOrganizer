# iRsetupOrganizer
The purpose of this tool is to organize the setup files located in the Downloads folder.

English:

- Remove all setup files (.sto) and zip files (from GO setups) from the "Downloads" directory.
  C:\Users\%userprofile%\Downloads

- Download the P1 or VRS setups (.sto file) or the GO zip files to your "Downloads" directory
  C:\Users\%userprofile%\Downloads

- VRS setups:
  - Start the ir_setup_organizer.exe, press 1 then the return key.
  - Now enter the iracing week without leading zero then press return key.
  - The setups will automatically be moved to the destination.

- P1 setups:
  - Start the ir_setup_organizer.exe, press 2 then the return key.
  - The setups will automatically be moved to the destination.
  
- GO setups:
  - Start the ir_setup_organizer.exe, press 3 then the return key.
  - Enter the setup week (1-12) when prompted.
  - The setups will be moved to a week subfolder below the season directory.
  
Problems?
- It may happen that the abbreviation for the car is not in the cars_directory_names_???.json file.
  You can add the missing abbreviation there and the script will find it.
