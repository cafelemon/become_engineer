(function () {
  "use strict";

  function init() {
    const marker = document.querySelector(".be-sample-tutor-mount[data-tutor-context-lesson]");
    if (!marker || marker.dataset.tutorInitialized === "true" || !window.BeTutorRuntime) return;
    const lessonId = marker.dataset.tutorContextLesson;
    const knowledgeUrl = new URL("../data/tutors/" + lessonId + ".json", window.location.href).href;
    window.BeTutorRuntime.init({
      marker: marker,
      lessonId: lessonId,
      knowledgeUrl: knowledgeUrl
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
