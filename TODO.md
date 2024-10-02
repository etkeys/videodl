
MVP:
- Combine "todo" table display and downloads/view.html table display.
- Admin add user
- About: Privacy
- About: Piracy
- About: Project, request feature/report bug
- Worker: Fail download if another item in the set completed and has same URL.
- Worker: Fail download if another item in the set completed and has same title.
- Make all routes use camelCase instead of snake_case.
- Local postgres database
- Migrations
- Recovery account (do after initial migrations setup)
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