function showNotification(id) {
    const allIds = ['hydeParkWarning', 'noMatchError', 'serverError'];
    allIds.forEach(hideNotification);
  
    const el = document.getElementById(id);
    if (el) el.classList.remove('is-hidden');
  }
  
  function hideNotification(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('is-hidden');
  }
  