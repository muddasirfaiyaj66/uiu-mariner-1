libcamera-vid --camera 0                 \
              -t 0                       \
              --inline -n                \
              --width 640 --height 480   \
              --framerate 30             \
              --codec h264               \
              --libav-format h264        \
              -o - |                     \
gst-launch-1.0 fdsrc ! h264parse !        \
              rtph264pay config-interval=1 pt=96 ! \
              udpsink host=192.168.125.27 port=5000
