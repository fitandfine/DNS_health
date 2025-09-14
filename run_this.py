#!/usr/bin/env python3
"""
DNS Health Checker GUI
Checks DNS records (A, AAAA, MX, CNAME) for a list of domains, measures latency, and displays results.
Ethical and fully cross-platform. No sniffing or incognito hacks.
"""

import sys
import time
import csv
from PyQt5 import QtWidgets, QtCore
import dns.resolver

class DNSChecker(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNS Health Checker")
        self.resize(800, 400)
        self.layout = QtWidgets.QVBoxLayout(self)

        # Input
        self.input_domains = QtWidgets.QPlainTextEdit()
        self.input_domains.setPlaceholderText("Enter one domain per line, e.g.\nexample.com\ngoogle.com")
        self.layout.addWidget(self.input_domains)

        # Buttons
        self.check_btn = QtWidgets.QPushButton("Check Domains")
        self.export_btn = QtWidgets.QPushButton("Export Results to CSV")
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.check_btn)
        btn_layout.addWidget(self.export_btn)
        self.layout.addLayout(btn_layout)

        # Table
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Domain", "A", "AAAA", "MX", "CNAME", "Latency(ms)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        # Connect signals
        self.check_btn.clicked.connect(self.check_domains)
        self.export_btn.clicked.connect(self.export_csv)

        # Results cache
        self.results = []

    def check_domains(self):
        self.table.setRowCount(0)
        self.results.clear()
        domains = [d.strip() for d in self.input_domains.toPlainText().splitlines() if d.strip()]
        for domain in domains:
            self.check_single_domain(domain)

    def check_single_domain(self, domain):
        resolver = dns.resolver.Resolver()
        row = []
        start_time = time.time()
        def query_record(record_type):
            try:
                answers = resolver.resolve(domain, record_type, lifetime=5)
                return ", ".join([r.to_text() for r in answers])
            except Exception:
                return "None"
        a = query_record("A")
        aaaa = query_record("AAAA")
        mx = query_record("MX")
        cname = query_record("CNAME")
        latency = round((time.time() - start_time)*1000, 1)
        row = [domain, a, aaaa, mx, cname, str(latency)]
        self.results.append(row)
        self.add_row(row)

    def add_row(self, row):
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, val in enumerate(row):
            self.table.setItem(r, c, QtWidgets.QTableWidgetItem(val))

    def export_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "dns_results.csv", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Domain", "A", "AAAA", "MX", "CNAME", "Latency(ms)"])
                    writer.writerows(self.results)
                QtWidgets.QMessageBox.information(self, "Export Complete", f"Results saved to {path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DNSChecker()
    window.show()
    sys.exit(app.exec_())
