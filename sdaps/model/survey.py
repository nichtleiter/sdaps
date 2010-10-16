# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <christoph.simon@gmx.eu>
# Copyright (C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bz2
import cPickle
import os

from sdaps import log

from sdaps.ugettext import ugettext, ungettext
_ = ugettext

# Force a certain set of options using slots
class Defs (object) :
	__slots__ = ["paper_width", "paper_height"]

class Survey (object) :

	def __init__ (self) :
		self.questionnaire = None
		self.sheets = list()
		self.title = unicode()
		self.info = dict()
		self.survey_id = 0
		self.questionnaire_ids = list()
		self.index = 0
		self.defs = Defs()

	def add_questionnaire (self, questionnaire) :
		self.questionnaire = questionnaire
		questionnaire.survey = self

	def add_sheet (self, sheet) :
		self.sheets.append(sheet)
		sheet.survey = self

	def calculate_survey_id (self) :
		import hashlib
		md5 = hashlib.new('md5')

		for qobject in self.questionnaire.qobjects :
			qobject.calculate_survey_id(md5)
		self.survey_id = 0
		# This compresses the md5 hash to a 32 bit unsigned value, by
		# taking the lower two bits of each byte.
		for i, c in enumerate(md5.digest()) :
			self.survey_id += bool(ord(c) & 1) << (2 * i)
			self.survey_id += bool(ord(c) & 2) << (2 * i + 1)

	@staticmethod
	def load (survey_dir) :
		file = bz2.BZ2File(os.path.join(survey_dir, 'survey'), 'r')
		survey = cPickle.load(file)
		file.close()
		survey.survey_dir = survey_dir
		return survey

	@staticmethod
	def new (survey_dir) :
		survey = Survey()
		survey.survey_dir = survey_dir
		return survey

	def save (self) :
		file = bz2.BZ2File(os.path.join(self.survey_dir, 'survey'), 'w')
		cPickle.dump(self, file, 2)
		file.close()

	def path (self, *path) :
		return os.path.join(self.survey_dir, *path)

	def new_path (self, path) :
		content = os.listdir(self.path())
		i = 1
		while path % i in content : i += 1
		return os.path.join(self.survey_dir, path % i)

	def get_sheet (self) :
		return self.sheets[self.index]

	sheet = property(get_sheet)

	def iterate (self, function, filter = lambda : True) :
		'''call function once for each sheet
		'''
		for self.index in range(len(self.sheets)) :
			if filter() : function()

	def iterate_progressbar (self, function, filter = lambda : True) :
		'''call function once for each sheet and display a progressbar
		'''
		print ungettext('%i sheet', '%i sheets', len(self.sheets)) % len(self.sheets)
		if len(self.sheets) == 0:
			return

		log.progressbar.start(len(self.sheets))

		for self.index in range(len(self.sheets)) :
			if filter() : function()
			log.progressbar.update(self.index + 1)

		print _('%f seconds per sheet') % (
			float(log.progressbar.elapsed_time) /
			float(log.progressbar.max_value)
		)

	def goto_sheet (self, sheet) :
		u'''goto the specified sheet object
		'''
		self.index = self.sheets.index(sheet)

	def goto_questionnaire_id (self, questionnaire_id) :
		u'''goto the sheet object specified by its questionnaire_id
		'''
		sheets = filter(
			lambda sheet: sheet.questionnaire_id == questionnaire_id,
			self.sheets
		)
		if len(sheets) == 1 :
			self.goto_sheet(sheets[0])
		else :
			raise ValueError

	def reset (self) :
		print 'DeprecationWarning'
		self.index = None

	def next (self) :
		print 'DeprecationWarning'
		if self.index == None :
			self.index = 0
		else :
			self.index += 1
		if self.index == len(self.sheets) :
			self.index = None
			return 0
		else :
			return 1

	def previous (self) :
		print 'DeprecationWarning'
		if self.index == None :
			self.index = len(self.sheets)-1
		else :
			self.index -= 1
		if self.index < 0 :
			self.index = None
			return 0
		else :
			return 1

	def goto (self, index) :
		print 'DeprecationWarning'
		if index >= 0 and index < len(self.sheets):
			self.index = index
			return 1
		else :
			self.index = None
			return 0

