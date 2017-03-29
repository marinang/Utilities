#!/usr/bin/python
# @file   Ganga.py
# @author Matthieu Marinangeli (matthieu.marinangeli@epfl.ch)
# @date   2017-02-14


def Resubmit(*argv):
	for j in argv:
		for sj in jobs(j).subjobs:
			 if sj.status == "failed":
				  sj.resubmit()
				
