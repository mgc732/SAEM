# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 10:18:11 2023

@author: Max
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///instance//bd_dicom.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

