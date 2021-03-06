import Component from '@ember/component';
import { mapBy, max, readOnly } from '@ember/object/computed';

export default Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,
  sumPilots: null,

  pilots: mapBy('years', 'pilots'),
  max: max('pilots'),
  sum: readOnly('sumPilots'),
});
