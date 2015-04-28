# ms-band-to-mfp
Python script for synching calories from Microsoft Health to MyFitnessPal

This script was put together pretty quickly and is a long way away from a 1.0.
I wanted a way for my Microsoft Band to tell MyFitnessPal exactly how many calories I was using each day.
This script solves this problem for me. 


* It is designed to be run as a cron job, regularly synching throughout the day.
* It is designed for Mac (directory structure, for example). It can easily be expanded or ported to support Linux, but Windows might be harder.
* It currently relies on Chrome cookies to access Microsoft Health and MyFitnessPal. An improvement would be to sign into each of these sites directly.
* It currently has to be run at 11:59PM at the end of the day in order to get an accurate total for the day. An improvement would be to reconcile yesterday before syncing today.


