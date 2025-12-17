window.addEventListener('DOMContentLoaded', event => {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  const counters = document.querySelectorAll('.counter');
  counters.forEach(counter => {
    const update = () => {
        const target = Number(counter.dataset.target);
        const value = Number(counter.innerText);
        const inc = target / 100;

        if (value < target) {
          counter.innerText = (value + inc).toFixed(2);
          setTimeout(update, 20);
        } else {
          counter.innerText = target;
          const stat = counter.closest('.stat');
          if (stat) {
            stat.classList.remove('high', 'medium', 'low');
            if (target >= 7.5) stat.classList.add('high');
            else if (target >= 6.5) stat.classList.add('medium');
            else stat.classList.add('low');
          }
        }
      };

      update();
  });



})