# File-Integrity-Monitor

A File Integrity Monitor (FIM) is a tool that scans files and stores their hashes. It then keeps on checking the hashes to compares the current state of those files to a previously recorded state. The FIM runs as a scheduled task, daemon or service. 

By default, this script starts with current directory as root directory and places all the hashes in the current directory.

