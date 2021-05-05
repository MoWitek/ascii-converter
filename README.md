This is an ASCII converter.
You can convert all possible things to ascii:
  - Videos
  - Images
  - Live Video
  
In the output there is the option of getting a rendered 
Image/Video or plain Text in the Terminal.


```
import mowiteks_asciilib
x = mowiteks_asciilib.core(height=64)

# renders image
x.render_img("neo.jpg", "neo-asciified.jpg")

# render video
x.render_video("badapple.avi", "badapple-aciified.avi")

# get life input from camera
x.live()
```
