#coding=UTF-8


import appModuleHandler
import displayModel
import queueHandler
import textInfos
import ui
import speech
import braille
import wx
import config
import re
import api
import controlTypes
from logHandler import log
from NVDAObjects.IAccessible import IAccessible

################
#IMPARA
################
class ChooseLesson(IAccessible) :
	listBox = {}
	def getListBox(self) :
		if len(self.listBox) == 0 :
			for ch in self.firstChild.next.firstChild.children :
				txt = ch.name
				self.listBox[txt.split(':')[0]] = txt
		return self.listBox

#Setto il valore dei pulsanti numerici con il loro corrispettivo nella listbox
class ChooseButton(IAccessible) :
	def _get_name(self) :
		orig = super(ChooseButton,self)._get_name()
		return self.parent.parent.getListBox()[orig]
#Esercizi sui tasti
class CharsEx(IAccessible) :
	def getContextInfo(self) :
		msg = self.name + '\r\n'
		msg = msg + "Battute esatte "+ self.getPunteggio() + "\r\n"
		msg = msg + "Prossima lettera "+ self.getNextChar()
		return msg
	
	def getNextChar(self) :
		text = u''
		text = self.firstChild.firstChild.value
		if text == None :
			text = u'spazio'
		else : 
			if text.isupper() : 
				text = text + " maiuscola"
		return text
		
	def getPunteggio(self) :
		info=displayModel.DisplayModelTextInfo(self,textInfos.POSITION_ALL)
		text = self.getTextList()
		punteggio = None
		for t in text :
			if re.match("^[0-9]+ [0-9]+$",t) :
				pt = t.split(' ')
				punteggio = pt[0] + " su " + pt[1]
		return punteggio
	
	def getTextList(self) :
		info=displayModel.DisplayModelTextInfo(self,textInfos.POSITION_ALL)
		return [block for block in info.getTextInChunks(textInfos.UNIT_LINE)]
	
	
class CharsExEdit(IAccessible) :
	origLevel = None
	def event_typedCharacter(self,ch) :
		if(self.checkMissChar()) :
			super(CharsExEdit,self).event_typedCharacter(ch)
			nextCh = self.parent.parent.getNextChar()
			speech.speakMessage(u'Errore  Hai scritto '+ch+'   scrivi '+self.appModule.expandAccent(nextCh))
			braille.handler.message(u'Errore  Hai scritto '+ch+'   scrivi '+ nextCh)
		else :
			super(CharsExEdit,self).event_typedCharacter(ch)
			nextCh = self.parent.parent.getNextChar()
			speech.speakMessage(self.appModule.expandAccent(nextCh))
			braille.handler.message("prossima lettera "+nextCh)
	
	def event_gainFocus(self) :
		#Incremento al massimo il livello di punteggiatura
		if (self.origLevel == None) :
			self.origLevel = config.conf["speech"]["symbolLevel"]
			config.conf["speech"]["symbolLevel"] = 300
		#Ripeto la prossima lettera
		ui.message(u"prossima lettera "+self.parent.parent.getNextChar())
	
	def event_loseFocus(self) :
		#Riporto il livello di punteggiatura a quello dell'utente
		config.conf["speech"]["symbolLevel"] = self.origLevel
	
	def checkMissChar(self) :
		return 'No! Hai scritto:' in self.parent.parent.getTextList()

#Esercizi con le frasi
class SentEx(IAccessible) :
	currentSentence = None
	def getContextInfo(self) :
		self.refreshSentences()
		msg = self.name + '\r\n'
		msg = msg + "Frase da scrivere "+ self.currentSentence + "\r\n"
		return msg
	
	def getNextChar(self,current) :
		self.refreshSentences()
		comlen = 0
		if current == None :
			comlen = 0
		else :
			comlen = len(current)
		if len(self.currentSentence) > comlen :
			next = self.currentSentence[comlen]
			if next == ' ' :
				next = 'spazio'
			elif next.isupper() :
				next = next + ' maiuscola'
			return self.appModule.expandAccent(next)
		return ''
	
	def refreshSentences(self) :
		deft = self.firstChild.next.next.firstChild
		if deft.role == controlTypes.ROLE_EDITABLETEXT :
			self.currentSentence = deft.windowText
		else : #F7
			self.currentSentence = self.firstChild.next.firstChild.windowText

class SentExEdit(IAccessible) :
	origLevel = None
	def event_typedCharacter(self,ch) :
		if(ch == ' ') :
			speech.speakMessage(self.value.split(' ')[-2])
		else :
			super(SentExEdit,self).event_typedCharacter(ch)
		speech.speakMessage(self.parent.parent.getNextChar(self.windowText))
	
	def sayWriteSentence(self) :
		return "Scrivi la frase " + self.parent.parent.currentSentence
	
	def showSentenceDialog(self):
		self.parent.parent.refreshSentences()
		txt = self.parent.parent.currentSentence
		wx.MessageBox(txt,"Scrivi la frase")
		
	def displaySentence(self) :
		wx.FutureCall(100, self.showSentenceDialog)
	
	def event_gainFocus(self) :
		#Incremento al massimo il livello di punteggiatura
		if (self.origLevel == None) :
			self.origLevel = config.conf["speech"]["symbolLevel"]
			config.conf["speech"]["symbolLevel"] = 300
		if (self.appModule.firstTimeSentence) : 
			self.appModule.firstTimeSentence = False
			self.displaySentence()
		else :
			#Ripeto la prossima lettera
			speech.speakMessage("prossima lettera "+self.parent.parent.getNextChar(self.value))
			super(SentExEdit,self).event_gainFocus()
			
	def event_loseFocus(self) :
		#Riporto il livello di punteggiatura
		config.conf["speech"]["symbolLevel"] = self.origLevel
	

################
#Altro
################
#TASTO = DITO
class TastoUgualeDito(IAccessible) :
	def initOverlayClass(self) :
		displayModel.requestTextChangeNotifications(self, True)
		
	def stopMonitoring(self) :
		displayModel.requestTextChangeNotifications(self, False)
		
	#Logica piu' precisa per getWinText
	def getWinText(self):
		mainwobj = self
		info=displayModel.DisplayModelTextInfo(mainwobj,textInfos.POSITION_ALL)
		#Escludo altro testo di oggetti diversi
		wrongLabels = [ch.name for ch in self.children]
		desclins = [block for block in info.getTextInChunks(textInfos.UNIT_LINE) if (not block in wrongLabels) and (len(block) > 1)]
		if len(desclins) > 1 :
			if desclins[-1] == desclins[-2] :
				desclins = desclins[:-1]
		return ''.join(desclins)
		
	def update(self) :
		ui.message(self.getWinText())
	
	def event_textChange(self):
		queueHandler.queueFunction(queueHandler.eventQueue, self.update)
		

#Altre videate...
#Videate generiche
class GenericThunderRT6FormDC(IAccessible) :
	cachedText = ''
	def forceWinText(self):
		self.parent.invalidateCache()
		self.parent.redraw()
		txt = self.obtainTrueText()
		if txt != None :
			self.cachedText = txt
			#in if non va in loop
			self.getWinText()
		#Mi arrendo
	
	def getWinText(self):
		if len(self.cachedText) > 1 :
			return self.cachedText
		txt = self.obtainTrueText()
		if(txt == None) :
			self.forceWinText()
		else :
			self.cachedText = txt
		return self.cachedText
		
	def obtainTrueText(self):
		info=displayModel.DisplayModelTextInfo(self,textInfos.POSITION_ALL)
		txt = info.text
		if (txt == None) :
			txt = ''
		#Escludo altro testo di oggetti diversi
		wrongLabels = [ch.name for ch in self.children if ch.name != None]
		for lab in wrongLabels :
			if(lab != None) :
				txt = txt.replace(lab,"")
		if(len(txt.replace(' ','')) == 0) :
			txt = None
		return txt


#BENVENUTO ...cominciamo bene...
class Welcome(IAccessible) :
	def getWinText(self) :
		info=displayModel.DisplayModelTextInfo(self,textInfos.POSITION_ALL)
		title = [block for block in info.getTextInChunks(textInfos.UNIT_LINE)][0]
		val = title + "\r\n"+ self.firstChild.firstChild.value
		return val
	

class FakeStaticTextBox(IAccessible) :
	def _get_name(self):
		return self.value
	def event_gainFocus(self):
		#Per il welcome sposto di default il focus sulla casella del nome
		if(isinstance(self.parent.parent,Welcome)) :
			self.parent.parent.setFocus()
			self.parent.next.next.firstChild.setFocus()
			return self.parent.next.next.firstChild.event_gainFocus()
		elif(self.parent.parent != None) and (self.parent.parent.name == self.appModule.TITLE_CHARORSENT) :
			self.parent.next.next.next.firstChild.setFocus()
			return self.parent.next.next.next.firstChild.event_gainFocus()
		else :
			super(FakeStaticTextBox,self).event_gainFocus()
	

class AppModule(appModuleHandler.AppModule):
	prevObj = None
	firstTimeSentence = True
	curPanelText = None
	spokenPanelName = None
	TITLE_TASTODITO = 'TASTO = DITO'
	TITLE_HELP = 'AIUTO!'
	TITLE_CHOOSELEC = 'SCELTA DELLA LEZIONE'
	TITLE_CHAREX = 'ESERCIZI SUI TASTI.'
	TITLE_SENTEX = 'ESERCIZI CON LE FRASI.'
	TITLE_CHARORSENT = 'CARATTERI O FRASI?'
	
	def expandAccent(self,text) :
		text = text.encode("utf8").replace("è","e accentata")
		text = text.replace("ò","o accentata")
		text = text.replace("é","e accentata con shift")
		text = text.replace("à","a accentata")
		text = text.replace("ù","u accentata")
		text = text.replace("ì","i accentata")
		text = text.replace("®","invio")
		return text
		
	def showContextInfoDialog(self):
		wx.MessageBox(api.getFocusObject().parent.parent.getContextInfo(),"Informazioni")
		
	def script_contextInfo(self,gesture) :
		if(isinstance(api.getFocusObject(),CharsExEdit) or isinstance(api.getFocusObject(),SentExEdit)):
			wx.FutureCall(1, self.showContextInfoDialog)
		else :
			gesture.send()
	__gestures = {
		"kb:f3": "contextInfo",
	}
	
	def event_gainFocus(self,obj,nextHandler) :
		if(isinstance(obj.parent.parent,GenericThunderRT6FormDC)) and ( self.spokenPanelName != obj.parent.parent.name) and (obj.parent.parent.name != None) and (obj.parent.parent.name != self.TITLE_HELP) :
			self.firstTimeSentence = True
			self.spokenPanelName = obj.parent.parent.name
			ui.message(obj.parent.parent.getWinText())
		elif isinstance(obj.parent.parent,Welcome) and self.spokenPanelName != 'WelcomeWin':
			ui.message(obj.parent.parent.getWinText())
			self.spokenPanelName = 'WelcomeWin'
		elif(obj.parent.parent != None and obj.parent.parent.windowClassName == 'ThunderRT6FormDC' and obj.parent.parent.name != None) :
			self.spokenPanelName = obj.parent.parent.name
		nextHandler()

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if (obj.windowClassName == 'ThunderRT6FormDC') and (obj.parent.windowClassName == 'ThunderRT6FormDC'):
			if (obj.name == self.TITLE_TASTODITO) :
				clsList.insert(0,TastoUgualeDito)
				if(self.prevObj != None) :
					self.prevObj.stopMonitoring()
				self.prevObj = obj
			elif (obj.name == None) and (obj.childCount > 1):
				clsList.insert(0,Welcome)
			elif obj.name == self.TITLE_CHOOSELEC :
				clsList.insert(0,ChooseLesson)
			elif obj.name != None and self.TITLE_CHAREX in obj.name :
				clsList.insert(0,CharsEx)
			elif obj.name != None and self.TITLE_SENTEX in obj.name :
				clsList.insert(0,SentEx)
			else :
				clsList.insert(0,GenericThunderRT6FormDC)
		else:
		#Fake textbox per box iniziale e messaggi di aiuto
			if (obj.windowClassName == 'ThunderRT6TextBox') and (isinstance(obj.parent.parent,Welcome) or (obj.parent.parent.name == self.TITLE_HELP)) :
				clsList.insert(0,FakeStaticTextBox)
			#Sposta il focus sul pulsante quando in scelta caratteri frasi
			elif (obj.windowClassName == 'ThunderRT6TextBox') and (obj.parent.parent.name == self.TITLE_CHARORSENT) :
				clsList.insert(0,FakeStaticTextBox)
			#Gestione pulsanti coi numeri gioco dell'oca
			elif (obj.windowClassName == "ThunderRT6CommandButton") and obj.name != None and (len(obj.name) <= 2) and isinstance(obj.parent.parent,ChooseLesson) :
				clsList.insert(0,ChooseButton)	
			#EditBox per esercizi caratteri e parole
			elif (obj.windowClassName == 'ThunderRT6TextBox') and (isinstance(obj.parent.parent,CharsEx) and obj.parent != obj.parent.parent.firstChild) :
				clsList.insert(0,CharsExEdit)
			elif (obj.windowClassName == 'ThunderRT6TextBox') and (isinstance(obj.parent.parent,SentEx)) and controlTypes.STATE_READONLY not in obj.states :
				clsList.insert(0,SentExEdit)