## Video DL

Version: {{ version_string }}
Last updated: {{ build_date_string }}

[TOC]

### About Video DL

This is a hobby project.
It is something I created because I've wanted to for years and my wife also needed the features this application provides.

#### Access

Access to this application is by **INVITE ONLY!**
If you want to send an invite to someone, please contact me.
I reserve the right to refuse or revoke access to anyone for any reason.

> **DO NOT** share you access token with others.
Everybody is given an access token that is specific to them.

### Using the application

#### Define a list to download

The <ins>To Do</ins> page is where you can stage many items to download.
You can add as many items that you want to the list.
Once you're ready for your items do be downloaded, use the *Submit* button to queue the entire list for download.

> **NOTE:** Once a collection of items has been submitted, you cannot change any items in that collection.

You don't need to have all the items you want in the same collection.
You can submit a collection items and create another collection while the first is downloading!

#### View queued collections and retrieve files

The <ins>Downloads</ins> page is where you can view all the collections of items that you have queued for download.
Here you can see the overall status and various other details about each collection.
Use the *View* button to see the details of all the items within a collection including their individual statuses.

A background service, "The Worker", will download each item in a collection one at a time.
Once all items have been processed, you can download a zip file that contains all the successfully downloaded items from the collection.

**Q: Why does The Worker pause after completing one download before starting the next?**  
**A:** You may notice that there is a delay from when one item in a collection is completed to when then next item starts downloading.
Or from when all items are completed to the entire collection becoming completed.
This is normal.
The Worker is configured to throttle traffic so as to not flood available bandwidth.

**Q: My collection is QUEUED, so why isn't it being processed?**  
**A:** The Worker sleeps most of the time.
It'll periodically wake up every few minutes to check is something needs doing.
It'll do the thing that needs doing, then go back to sleep.
Having said that, there are a couple other things that may keep your collection QUEUED for a longer period of time.

1. The Worker can only process one collection at a time and only one item from
    within that one collection at a time.
It could be that another user has a collection that is currently being processed and cannot process your's
    at the moment.
The Worker process collections and items within collections if a "First Come, First Served"
    manner, or "Oldest First".
You'll need to wait until your collection is the oldest in the queue.

1. The Worker is not running. This could be due to maintenance or it crashed.
If you feel that this may be the case, please contact me.


### Disclaimers

#### Privacy

No shilling.
No adds.
No malware.

I'm not going to sell your data.
Your data within this application is only kept for a short time.
Exceptions to this are your name and email, because I need those to identify you for administrative reasons.

#### Piracy

Downloading copyright protected media without permission or paying for it is illegal.
I won't stop you from downloading copyright protected media because I don't know if you have permission or if you've already purchased the content.

Stealing is bad, okay?


### Bug Reports and Feature Requests

App not behaving in a way you expected?
Should the app do something new?
Please contact me.
