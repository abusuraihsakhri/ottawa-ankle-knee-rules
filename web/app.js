/* Ottawa radiography criteria: deterministic, offline and intentionally non-diagnostic. */
(function (root) {
  'use strict';
  const labels = {
    posterior_lateral_malleolus_tenderness: 'Bony tenderness at posterior edge (distal 6 cm) or tip of lateral malleolus',
    posterior_medial_malleolus_tenderness: 'Bony tenderness at posterior edge (distal 6 cm) or tip of medial malleolus',
    navicular_tenderness: 'Bony tenderness at navicular',
    fifth_metatarsal_base_tenderness: 'Bony tenderness at base of fifth metatarsal',
    fibular_head_tenderness: 'Bony tenderness at fibular head',
    isolated_patellar_tenderness: 'Isolated bony tenderness at patella',
    cannot_flex_90: 'Unable to flex knee to 90°',
    unable_four_steps_immediately: 'Unable to take four weight-bearing steps immediately after injury',
    unable_four_steps_at_assessment: 'Unable to take four weight-bearing steps at clinical assessment',
    age_55_or_over: 'Age ≥55 years (knee rule)',
    unable_four_steps_both_times: 'Unable to take four steps both immediately and at assessment'
  };
  const fields = {
    ankle: ['posterior_lateral_malleolus_tenderness', 'posterior_medial_malleolus_tenderness'],
    midfoot: ['navicular_tenderness', 'fifth_metatarsal_base_tenderness'],
    knee: ['fibular_head_tenderness', 'isolated_patellar_tenderness', 'cannot_flex_90']
  };
  const walking = ['unable_four_steps_immediately', 'unable_four_steps_at_assessment'];
  const messages = {
    radiography_indicated: 'Radiography indicated by the Ottawa rule',
    radiography_not_indicated: 'Radiography not indicated by the Ottawa rule',
    insufficient_information: 'Assessment incomplete',
    not_applicable: 'Rule not applicable'
  };

  function evaluate(data) {
    if (!Object.prototype.hasOwnProperty.call(fields, data.site)) throw Error('Invalid injury site');
    if (!Number.isInteger(data.age) || data.age < 0 || data.age > 120) throw Error('Enter a valid age (0–120 years).');
    if (['pain_present', 'acute_blunt_trauma', 'reliable_exam'].some(k => typeof data[k] !== 'boolean')) throw Error('Complete the eligibility questions.');
    const applicable = data.age >= 18 && data.pain_present && data.acute_blunt_trauma && data.reliable_exam;
    if (!applicable) {
      return {outcome: 'not_applicable', positives: [], missing: [], message: messages.not_applicable};
    }
    const relevant = [...fields[data.site], ...walking];
    for (const k of relevant) {
      if (!(data[k] === true || data[k] === false || data[k] === null || data[k] === undefined)) throw Error('Invalid finding: ' + k);
    }
    const positives = fields[data.site].filter(k => data[k] === true);
    if (data.site === 'knee' && data.age >= 55) positives.unshift('age_55_or_over');
    const first = data[walking[0]], second = data[walking[1]];
    if (first === true && second === true) positives.push('unable_four_steps_both_times');
    let missing = relevant.filter(k => data[k] == null);
    if (first === false || second === false) missing = missing.filter(k => !walking.includes(k));
    const outcome = positives.length ? 'radiography_indicated' : missing.length ? 'insufficient_information' : 'radiography_not_indicated';
    return {outcome, positives, missing, message: messages[outcome]};
  }

  function init(doc) {
    const form = doc.getElementById('assessment');
    const site = doc.getElementById('site');
    const findings = doc.getElementById('findings');
    const result = doc.getElementById('result');
    const download = doc.getElementById('download');
    let last = null;
    function choice(name, title) {
      const div = doc.createElement('div'); div.className = 'question';
      const label = doc.createElement('label'); label.htmlFor = name; label.textContent = title;
      const select = doc.createElement('select'); select.id = name; select.name = name;
      [['', 'Not assessed'], ['yes', 'Yes'], ['no', 'No']].forEach(([value, text]) => {
        const option = doc.createElement('option'); option.value = value; option.textContent = text; select.appendChild(option);
      });
      div.append(label, select); return div;
    }
    function renderFindings() {
      findings.replaceChildren();
      for (const key of [...fields[site.value], ...walking]) findings.appendChild(choice(key, labels[key]));
      last = null; download.disabled = true;
      result.textContent = 'Complete the criteria and select Evaluate.';
      result.dataset.outcome = '';
    }
    site.addEventListener('change', renderFindings);
    form.addEventListener('reset', () => root.setTimeout(renderFindings, 0));
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      const data = {site: site.value, age: Number(doc.getElementById('age').value)};
      for (const key of ['pain_present', 'acute_blunt_trauma', 'reliable_exam', ...fields[data.site], ...walking]) {
        const value = doc.getElementById(key).value;
        data[key] = value === 'yes' ? true : value === 'no' ? false : null;
      }
      try {
        // Treat an empty age field differently from zero.
        if (!doc.getElementById('age').value.trim()) throw Error('Enter age in years.');
        last = evaluate(data);
        result.replaceChildren();
        const heading = doc.createElement('strong'); heading.textContent = last.message;
        const note = doc.createElement('p');
        note.textContent = last.outcome === 'radiography_indicated'
          ? 'Positive criteria: ' + last.positives.map(k => labels[k]).join('; ') + '. Clinical judgment remains necessary.'
          : last.outcome === 'radiography_not_indicated'
            ? 'All required findings were assessed and negative. Reassess if symptoms worsen or clinical concern persists.'
            : last.outcome === 'insufficient_information'
              ? 'Not assessed: ' + last.missing.map(k => labels[k]).join('; ') + '. No negative decision can be made.'
              : 'Use an alternative assessment when under 18, outside an acute traumatic presentation, outside the selected pain zone, or when examination is unreliable.';
        result.append(heading, note);
        result.dataset.outcome = last.outcome;
        download.disabled = false;
      } catch (err) {
        last = null; download.disabled = true; result.textContent = err.message; result.dataset.outcome = 'error';
      }
    });
    download.addEventListener('click', function () {
      if (!last) return;
      const blob = new Blob([JSON.stringify({site: site.value, ...last}, null, 2) + '\n'], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = doc.createElement('a'); a.href = url; a.download = 'ottawa-rule-assessment.json'; a.click();
      root.setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    renderFindings();
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = {evaluate, fields, labels};
  if (root.document) root.document.addEventListener('DOMContentLoaded', () => init(root.document));
})(typeof window === 'undefined' ? globalThis : window);
