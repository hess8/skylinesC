import Component from '@ember/component';

export default Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-striped', 'table-condensed', 'table-flights'],

  groupflights: null,
  showDate: true,
  showAirport: true,
  showClub: true,
});
