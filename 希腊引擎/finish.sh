cd /workspace/work/argus
while [ $(pgrep -f "film.py --part" | wc -l) -gt 0 ]; do sleep 20; done
printf "file 'part0.mp4'\nfile 'part1.mp4'\nfile 'part2.mp4'\nfile 'part3.mp4'\n" > vid/list.txt
ffmpeg -v error -y -f concat -safe 0 -i vid/list.txt -i out/mix.wav -map 0:v -map 1:a -vf fps=24 -c:v libx264 -profile:v high -level 4.1 -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/argus_final.mp4 && cp /tmp/argus_final.mp4 /workspace/work/argus/argus_final.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,avg_frame_rate,level -show_entries format=duration -of compact /workspace/work/argus/argus_final.mp4
