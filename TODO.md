
MVP:
- Test site configuration
    - postgres port will need to be different to not collide with production
    - App port will need to be different to not collide with production
- Production site configuration

After MVP:
- App settings
- Worker read from app settings
- Admin stop worker
- Admin should not have "Add all to To Do" for other users (when download set
  is packing failed)
- Fix mutable global variables (runtime_context)
- Implement inactivating a user. Also terminate any downloads in progress and
  future
- Combine "todo" table display and downloads/view.html table display.
- Make page stylings better. Currently everything is left aligned and two-thirds
  of the page.
- Make site mobile/small device friendly
- Bug: While processing items, when the status of an item changes, it gets sent
  to the bottom of the list. [This is how postgres works](https://dba.stackexchange.com/a/259825)