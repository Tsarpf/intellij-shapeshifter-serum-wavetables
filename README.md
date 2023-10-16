Created with the help of GPT-4 while very tired, so don't expect beautiful code.

Use at your own risk!!! 
You may for example:
- Destroy your OS by accidentally writing random binary stuff to the middle of a critical file
- Destroy your Shapeshifter by writing something where you shouldn't have and running that firmware

The writer also handles fixing the `.jic` file checksum so it works with Quartus (first time I've heard anyone solve this!). So no need to use the super slow Terasic writer with the raw EPCS dump

The offsets in the binary file seem to sometimes change between firmware versions, so be sure to set the offsets to match your firmware version binary format.
