
MVP:
- Worker: Fail download if another item in the set completed and has same URL.
- Make all routes use camelCase instead of snake_case.
- Local postgres database
- Migrations
- Recovery account (do after initial migrations setup; seed this account)
- Worker: Fail download if another item in the set completed and has same title.
  (required model change; do after migrations are setup)
- Worker: vary the sleep time between downloading items.
- App: SystemD service
- Worker: SystemD service
- Test site configuration
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