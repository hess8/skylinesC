import { visit, click, currentURL, fillIn, waitFor, stop, pauseTest } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { percySnapshot } from 'ember-percy';
import { authenticateSession, currentSession } from 'ember-simple-auth/test-support';

import { setupPolly } from 'skylines/tests/helpers/setup-polly';

module('Acceptance | Settings | Create Club', function(hooks) {
  setupApplicationTest(hooks);
  setupPolly(hooks, { recordIfMissing: false });

  function isAuthenticated() {
    return Boolean(currentSession().data.authenticated.settings);
  }

  test('users can create a club', async function(assert) {
    let { server } = this.polly;

    let settings = {
      id: 123,
      firstName: 'John',
      lastName: 'Doe',
      name: 'John Doe',
      email: 'john@doe.com',

      altitudeUnit: 0,
      distanceUnit: 1,
      liftUnit: 0,
      speedUnit: 1,
    };

// these set up server responses for requests from ember/js.
    server.get('/api/settings').intercept((req, res) => {
      res.status(200);
      res.json(settings);
      console.log('Wish this would work')
    });

    server.post('/api/users/check-email').intercept((req, res) => {
      res.status(200);
      res.json({ result: 'self' });
    });

    server.post('/api/settings/password/check').intercept((req, res) => {
      let json = JSON.parse(req.body);
      let result = json.password === 'secret123';
      res.status(200);
      res.json({ result });
    });

    server.post('/api/settings/club').intercept((req, res) => {
      let json = JSON.parse(req.body);
      let result = json.password === 'secret123';
      res.status(200);
      res.json({ result });
    });


    await authenticateSession({ settings });
    assert.ok(isAuthenticated());

    // visit the front page
    await visit('/');
    await percySnapshot('Index');

    // open the menu
    await click('[data-test-nav-bar] [data-test-user-menu-dropdown] [data-test-toggle]');
    await waitFor('[data-test-nav-bar] [data-test-user-menu-dropdown] [role="menu"]');

    // click on the "Settings" link
    await click('[data-test-nav-bar] [data-test-user-menu-dropdown] [role="menu"] [data-test-setting-link]');
    assert.equal(currentURL(), '/settings/profile');
    await percySnapshot('Settings');

    // click on the "Group" button

    await click('[data-test-group]');
    console.log('Did click group/club')
    await pauseTest()
//    it's failing because we have to set up data for the club page!!!
    assert.equal(currentURL(), '/settings/club');

  });
});
