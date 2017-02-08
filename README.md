# MoneyMeExportPython

This tool extracts data from a backup file of the MoneyMe app for Android.
It creates a CSV file with a format that is suitable for me :)

This is a Pyhton port of https://github.com/maxicombina/MoneyMeExport.

## So... why does this port exist?
Basically, I wrote the original tool in C# using Monodevelop... what could go wrong? Thanks to the magic of the VMs it should work everywhere, right?
It was a really painful experience. I wanted to use the Mono VM, not the .NET, because I wanted the tool to be portable.
Using sqlite for Mono is painful, poorly documented.
Whenever I want to checkout the code in a new Windows box, I have to install tons of software (Mono, Monodevelop/Xamarin, GTK# for windows --this I understand but mention it anyway because it adds up, etc). In my latest attempt on a Windows 10 box, I had to install some "Microsoft build tools 2013". After that, Monodevelop kept complaining and wanted "Microsoft build tools 2015".
When I finally could open the project, and configure it (again... in every checkout I have to do it) to use the Mono VM, the compilation just ended with "Error, see the log for details". Nothing more. No useful messages. Thanks for that!
In the web people talked about "the .NET version", so I tried with 4, 4.5, 4.5.1, I even think I saw a 4.6.1 or so.

At the end, I gave up. This is a very simple tool, and should take no more than 5 minutes to download and re-build.

I am sure that eventually I would have got it. But as my latest attempt in a Windows 10 box showed, the process is really cumbersome and changes with every new release of Windows, Mono, and so on.

## Welcome Pyhton
I am not a professional Pyhton developer. I use it to hack quick scripts from time to time.
I really like Pyhton, so I decided to take a look at how easy/difficult this could be.
I installed Pyhton in a Windows box (in Linux it is really straightforward). Very easy: go to a web page, download an installer, install. That's it.
It has sqlite3 support. It parses arguments automagically. Progamming Pyhton is quick and fun.
In a couple of hours (most of them learning how to do specific stuff in Pyhton) I ported the tool. I know, it has no GUI, but I don't care right now.
The only problem I found so far is that the `print()' function encodes in 'ascii' instead of something more useful. Easy to workaround, but I still don't know a «good» way to do this.
All in all, if I want to use the tool in another box, it is only matter of installing Pyhton (if not already there) and run it! No extra software, no sqlite3 driver, no strange VM configs :)
