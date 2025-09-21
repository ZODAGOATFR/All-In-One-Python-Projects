from tkinter import *
import datetime
import time
import os
from threading import *

root = Tk()
root.geometry("400x200")

def Threading():
	t1=Thread(target=alarm)
	t1.start()

def alarm():
	while True:
		set_alarm_time = f"{hour.get()}:{minute.get()}:{second.get()}"
		time.sleep(1)
		current_time = datetime.datetime.now().strftime("%H:%M:%S")
		print(current_time,set_alarm_time)

		if current_time == set_alarm_time:
			print("Time to Wake up")
			os.system("afplay sound.wav") 
Label(root,text="Alarm Clock",font=("Helvetica 20 bold"),fg="red").pack(pady=10)
Label(root,text="Set Time",font=("Helvetica 15 bold")).pack()

frame = Frame(root)
frame.pack()

hour = StringVar(root)
hours = tuple(f"{i:02}" for i in range(24)) 
hour.set(hours[0])

hrs = OptionMenu(frame, hour, *hours)
hrs.pack(side=LEFT)

minute = StringVar(root)
minutes = tuple(f"{i:02}" for i in range(60))
minute.set(minutes[0])

mins = OptionMenu(frame, minute, *minutes)
mins.pack(side=LEFT)

second = StringVar(root)
seconds = tuple(f"{i:02}" for i in range(60))
second.set(seconds[0])

secs = OptionMenu(frame, second, *seconds)
secs.pack(side=LEFT)

Button(root,text="Set Alarm",font=("Helvetica 15"),command=Threading).pack(pady=20)
root.mainloop()
