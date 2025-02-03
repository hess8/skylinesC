import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | landscapes/convert', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:landscapes/convert');
    assert.ok(route);
  });
});
