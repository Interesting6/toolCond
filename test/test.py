import re

topic = "ECCI/WbQFj3A6FhvHpWuJoBgYNL/8cwH3zaAWEwLPTB9XSHJNE/app/irons-1/save-1"

sender = re.findall(r'^ECCI/.*/.*/.*/(.*)/.*',topic)[0]
print(sender)