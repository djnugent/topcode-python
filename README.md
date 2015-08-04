--------------------------------------------
Tangible Object Placement Codes (TopCodes)
--------------------------------------------

This package contains a simple computer vision library for identifying
a collection of tagged objects on a flat surface.  For each object,
position, angular orientation, and an ID number are also provided.

The TopCode symbol format is a simplifed version of TRIP 
(de Ipina, Mendonca, and Hopper. UbiComp, 2006).

To get started:

1. Download and install the Java JDK (http://download.java.net/jdk6)


2. Download and install Apache Ant  (http://ant.apache.org)

   Remember to set the ANT_HOME and JAVA_HOME environment variables. 


3. Extract the TopCode library on your local machine.


4. Open a shell and go to the directory where you extracted the TopCodes source.


5. Run the ant build script:

     > ant build

   After about 10 seconds, it should say BUILD SUCCESSFUL and return
   you to the command prompt. 


6. Assuming everything went according to plan, there are two basic
   commands that are useful. Assuming you’re still in the TopCodes
   directory that you installed, they are:

    > java -cp classes topcodes.TopCodePrinter

   This creates a sheet of TopCodes which can then be printed by typing
   Ctrl + p.

   > java -cp classes topcodes.DebugWindow

   This allows you to test the library on an image.  The basic key
   commands are:

      Ctrl + O      Open a JPEG file
      +             Zoom in
      -             Zoom out
      b             See the image after thresholding
      t             Show / hide topcode annotations

      Clicking and dragging with the mouse will pan the image.
      All of the TopCode ID numbers will be printed on the command
      line each time an image is loaded. 


===========================================================

This is a list of valid TopCode ID numbers:

0 0000 0001 1111  = 31
0 0000 0010 1111  = 47
0 0000 0011 0111  = 55
0 0000 0011 1011  = 59
0 0000 0011 1101  = 61
0 0000 0100 1111  = 79
0 0000 0101 0111  = 87
0 0000 0101 1011  = 91
0 0000 0101 1101  = 93
0 0000 0110 0111  = 103
0 0000 0110 1011  = 107
0 0000 0110 1101  = 109
0 0000 0111 0011  = 115
0 0000 0111 0101  = 117
0 0000 0111 1001  = 121
0 0000 1000 1111  = 143
0 0000 1001 0111  = 151
0 0000 1001 1011  = 155
0 0000 1001 1101  = 157
0 0000 1010 0111  = 167
0 0000 1010 1011  = 171
0 0000 1010 1101  = 173
0 0000 1011 0011  = 179
0 0000 1011 0101  = 181
0 0000 1011 1001  = 185
0 0000 1100 0111  = 199
0 0000 1100 1011  = 203
0 0000 1100 1101  = 205
0 0000 1101 0011  = 211
0 0000 1101 0101  = 213
0 0000 1101 1001  = 217
0 0000 1110 0011  = 227
0 0000 1110 0101  = 229
0 0000 1110 1001  = 233
0 0000 1111 0001  = 241
0 0001 0000 1111  = 271
0 0001 0001 0111  = 279
0 0001 0001 1011  = 283
0 0001 0001 1101  = 285
0 0001 0010 0111  = 295
0 0001 0010 1011  = 299
0 0001 0010 1101  = 301
0 0001 0011 0011  = 307
0 0001 0011 0101  = 309
0 0001 0011 1001  = 313
0 0001 0100 0111  = 327
0 0001 0100 1011  = 331
0 0001 0100 1101  = 333
0 0001 0101 0011  = 339
0 0001 0101 0101  = 341
0 0001 0101 1001  = 345
0 0001 0110 0011  = 355
0 0001 0110 0101  = 357
0 0001 0110 1001  = 361
0 0001 0111 0001  = 369
0 0001 1000 0111  = 391
0 0001 1000 1011  = 395
0 0001 1000 1101  = 397
0 0001 1001 0011  = 403
0 0001 1001 0101  = 405
0 0001 1001 1001  = 409
0 0001 1010 0011  = 419
0 0001 1010 0101  = 421
0 0001 1010 1001  = 425
0 0001 1011 0001  = 433
0 0001 1100 0101  = 453
0 0001 1100 1001  = 457
0 0001 1101 0001  = 465
0 0010 0010 0111  = 551
0 0010 0010 1011  = 555
0 0010 0010 1101  = 557
0 0010 0011 0011  = 563
0 0010 0011 0101  = 565
0 0010 0011 1001  = 569
0 0010 0100 0111  = 583
0 0010 0100 1011  = 587
0 0010 0100 1101  = 589
0 0010 0101 0011  = 595
0 0010 0101 0101  = 597
0 0010 0101 1001  = 601
0 0010 0110 0011  = 611
0 0010 0110 0101  = 613
0 0010 0110 1001  = 617
0 0010 1000 1011  = 651
0 0010 1000 1101  = 653
0 0010 1001 0011  = 659
0 0010 1001 0101  = 661
0 0010 1001 1001  = 665
0 0010 1010 0011  = 675
0 0010 1010 0101  = 677
0 0010 1010 1001  = 681
0 0010 1100 1001  = 713
0 0011 0001 1001  = 793
0 0011 0010 0101  = 805
0 0011 0010 1001  = 809
0 0011 0100 1001  = 841
0 0100 1001 0011  = 1171
0 0100 1001 0101  = 1173
0 0100 1010 0101  = 1189
99 codes.