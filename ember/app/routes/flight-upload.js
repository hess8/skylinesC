import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
  ajax: service(),
  account: service(),

  async model() {
    let ajax = this.ajax;
    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = [];
    if (clubId) {
      let { users } = await ajax.request(`/api/users?club=${clubId}`);
      clubMembers = users.filter(user => user.id !== accountId);
    }
    else{
    alert("You haven't joined a group, so your flight won't be in any group flights.  If you're not part of a real group and want to stop this message, in Settings join the group called 'No Group'")
    }

    return { clubMembers };
  },



  setupController(controller) {
    this._super(...arguments);

    controller.set('result', null);
  },
});
