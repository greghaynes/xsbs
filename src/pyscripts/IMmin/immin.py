from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber.xmlstream import XmlStreamFactory, XmlStream
from twisted.words.protocols.jabber import client, jid
from twisted.words.xish import domish
from twisted.internet import reactor

from xsbs.settings import PluginConfig
from xsbs.commands import commandHandler

import logging

config = PluginConfig('im')
jabber_enable = config.getOption('Jabber', 'enable', 'no') == 'yes'
jabber_server = config.getOption('Jabber', 'server', 'server.com')
jabber_port = config.getOption('Jabber', 'port', '5222')
jabber_id = config.getOption('Jabber', 'jid', 'user@server.com')
jabber_pass = config.getOption('Jabber', 'password', 'pass')
jabber_alerts = config.getOption('Jabber', 'alert_accounts', 'admin1@server.com, admin2@otherserver.com')
del config
jabber_port = int(jabber_port)
jabber_id += '/xsbs'
jabber_alerts = jabber_alerts.strip().split(',')

class JabberClient(XmlStream):
	def connectionMade(self):
		logging.debug('Connected')
		self.addObserver(
			xmlstream.STREAM_AUTHD_EVENT,
			self.authenticated
			)
		XmlStream.connectionMade(self)
	def connectionLost(self, reason):
		logging.debug('Connection lost: %s' % reason)
		self.factory.clientLost(self)
	def authenticated(self, data):
		logging.debug('Authenticated')
		self.factory.clientAuthenticated(self)
	def message(self, to, message):
		msg = domish.Element(('jabber:client','message'))
		msg["to"] = jid.JID(to).full()
		msg["from"] = jid.JID(jabber_id).full()
		msg["type"] = "chat"
		msg.addElement("body", "jabber:client", message)
		self.send(msg)

class JabberClientFactory(XmlStreamFactory):
	protocol = JabberClient
	clients = []
	def clientAuthenticated(self, client):
		if client not in self.clients:
			self.clients.append(client)
	def clientLost(self, client):
		if client in self.clients:
			self.clients.remove(client)
	def message(self, to, message):
		for client in self.clients:
			client.message(to, message)

myJid = jid.JID(jabber_id)
factory = JabberClientFactory(client.BasicAuthenticator(myJid, jabber_pass))

if jabber_enable:
	reactor.connectTCP(jabber_server, jabber_port, factory)

@commandHandler('ops')
def ping(cn, args):
	p = player(cn)
	message = 'Player \'%s\' (%s) issued ops command: %s' % (
		p.name(),
		p.ipString(),
		args
		)
	for alert in jabber_alerts:
		factory.message(alert, message)

