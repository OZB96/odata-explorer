from burp import IBurpExtender, ITab, IExtensionStateListener
from javax.swing import JPanel, JButton, JTextArea, JScrollPane, BoxLayout
from java.awt import BorderLayout, Dimension
import javax.swing.JOptionPane as JOptionPane
import xml.dom.minidom as minidom
import json
from java.awt.event import ActionListener

class ButtonClickListener(ActionListener):
    def __init__(self, extender):
        self.extender = extender

    def actionPerformed(self, event):
        metadata_text = self.extender.metadata_area.getText()
        try:
            data = self.extender.format_data(self.extender.generate_requests(metadata_text))
        except Exception as e:
            JOptionPane.showMessageDialog(None, "Error: {}".format(str(e)), "Error", JOptionPane.ERROR_MESSAGE)
            return

        formatted_data = "".join(str(element) + "\n" for element in data)
        self.extender.result_area.setText(formatted_data)

class BurpExtender(IBurpExtender, ITab, IExtensionStateListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Enhanced OData Explorer")
        self.init_gui()
        callbacks.addSuiteTab(self)
        callbacks.registerExtensionStateListener(self)

    def init_gui(self):
        self.main_panel = JPanel(BorderLayout())

        self.generate_button = JButton("Generate Requests")
        button_click_listener = ButtonClickListener(self)
        self.generate_button.addActionListener(button_click_listener)
        self.main_panel.add(self.generate_button, BorderLayout.NORTH)

        self.content_panel = JPanel()
        self.content_panel.setLayout(BoxLayout(self.content_panel, BoxLayout.X_AXIS))
        self.main_panel.add(self.content_panel, BorderLayout.CENTER)

        self.metadata_area = JTextArea("Insert metadata XML here!")
        self.metadata_scroll = JScrollPane(self.metadata_area)
        self.metadata_scroll.setPreferredSize(Dimension(400, 200))
        self.content_panel.add(self.metadata_scroll)

        self.result_area = JTextArea()
        self.result_scroll = JScrollPane(self.result_area)
        self.result_scroll.setPreferredSize(Dimension(400, 200))
        self.content_panel.add(self.result_scroll)

    def generate_requests(self, metadata_xml):
        dom = minidom.parseString(metadata_xml)
        service_url = dom.getElementsByTagName("ServiceDocument")[0].getAttribute("xml:base")

        http_requests = []
        for entity in dom.getElementsByTagName("EntitySet"):
            name = entity.getAttribute("Name")
            url = f"{service_url}/{name}"
            for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "MERGE"]:
                http_requests.append({"method": method, "url": url, "parameters": {}})

        return http_requests

    def format_data(self, data):
        requests = []
        for row in data:
            method = row["method"]
            url = row["url"]
            request = f"{method} {url} HTTP/1.1\r\nHost: your-odata-service-url\r\n\r\n"
            requests.append(request)

        return requests

    def getTabCaption(self):
        return "Enhanced OData Explorer"

    def getUiComponent(self):
        return self.main_panel
