/* taplai clone: static site has no server-side exam session.
   Turn the "chọn hạng + đề" form into a client-side redirect to a
   pre-generated đề page: /thi-thu-ly-thuyet-hang-<class>-de-chuan?de=<n> */
(function () {
    'use strict';
    var counts = {};
    try {
        (document.CLASS_LIST || []).forEach(function (c) { counts[c.id] = c.exams; });
    } catch (e) {}

    function slug(v) { return String(v || '').toLowerCase(); }

    function pickExam(cls, requested) {
        var max = counts[cls] || 14;
        var n = parseInt(requested, 10);
        if (!n || n < 1 || n > max) n = 1 + Math.floor(Math.random() * max);
        return n;
    }

    document.addEventListener('submit', function (e) {
        var f = e.target;
        if (!f || f.id !== 'frmExam') return;
        var classSel = f.querySelector('select[name=class]');
        var examSel = f.querySelector('select[name=exam]');
        var cls = classSel ? classSel.value : (document.SELECTED_CLASS_NEW || 'B');
        if (!cls) return;
        e.preventDefault();
        var n = pickExam(cls, examSel ? examSel.value : 0);
        try { localStorage.setItem('SELECTED_CLASS_NEW', cls); } catch (err) {}
        window.location.href = '/thi-thu-ly-thuyet-hang-' + slug(cls) + '-de-chuan?de=' + n;
    }, true);
})();
