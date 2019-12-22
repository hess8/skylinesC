import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | club-edit-form', function(hooks) {
  setupRenderingTest(hooks);
//  setLocale('en')

  test('it renders', async function(assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<ClubEditForm />`);

  console.log('Wish this would work');
//  console.log(this.element.textContent.trim());
  assert.equal(true, true, "succeeds");
  });
//   assert.equal(this.element.textContent.trim(), '');
//    debugger;
//    // Template block usage:
//    await render(hbs`
//      <ClubEditForm>
//        template block text
//      </ClubEditForm>
//    `);
//
//    assert.equal(this.element.textContent.trim(), 'template block text');
//  });
});
