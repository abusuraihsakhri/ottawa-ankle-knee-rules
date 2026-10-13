const assert = require('node:assert/strict');
const {evaluate, fields} = require('./app.js');
let n = 0;
const base = {age: 38, site: 'ankle', pain_present: true, acute_blunt_trauma: true, reliable_exam: true,
  unable_four_steps_immediately: false, unable_four_steps_at_assessment: false};
function check(site, more = {}) {return evaluate({...base, site, ...Object.fromEntries(fields[site].map(k => [k,false])), ...more});}
for (const site of Object.keys(fields)) {
  assert.equal(check(site).outcome, 'radiography_not_indicated'); n++;
  for (const criterion of fields[site]) {assert.equal(check(site,{[criterion]:true}).outcome,'radiography_indicated'); n++;}
  assert.equal(check(site,{unable_four_steps_immediately:true,unable_four_steps_at_assessment:true}).outcome,'radiography_indicated'); n++;
  assert.equal(check(site,{unable_four_steps_immediately:true,unable_four_steps_at_assessment:false}).outcome,'radiography_not_indicated'); n++;
}
assert.equal(check('knee',{age:55}).outcome,'radiography_indicated');n++;
assert.equal(check('knee',{age:54}).outcome,'radiography_not_indicated');n++;
assert.equal(check('ankle',{posterior_lateral_malleolus_tenderness:null}).outcome,'insufficient_information');n++;
assert.equal(check('knee',{age:55,fibular_head_tenderness:null}).outcome,'radiography_indicated');n++;
assert.equal(check('midfoot',{age:17}).outcome,'not_applicable');n++;
assert.equal(check('ankle',{reliable_exam:false}).outcome,'not_applicable');n++;
assert.equal(check('ankle',{pain_present:false}).outcome,'not_applicable');n++;
assert.equal(check('ankle',{acute_blunt_trauma:false}).outcome,'not_applicable');n++;
assert.throws(()=>check('knee',{age:NaN}));n++;
console.log(n + ' browser-rule assertions passed');
