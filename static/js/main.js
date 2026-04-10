/* ═══════════════════════════════════════════════
   Maram – Main JavaScript
   ═══════════════════════════════════════════════ */

$(document).ready(function () {

  // ── Sidebar toggle ──────────────────────────────
  $('#sidebarToggle').on('click', function () {
    const sidebar = $('#sidebar');
    if ($(window).width() <= 768) {
      sidebar.toggleClass('mobile-open');
    } else {
      sidebar.toggleClass('collapsed');
    }
  });

  // ── Auto-dismiss alerts after 5 s ──────────────
  setTimeout(function () {
    $('.alert.fade.show').alert('close');
  }, 5000);

  // ── Notification polling (every 60 s) ──────────
  function updateNotifBadge(data) {
    const badge  = $('#notifBadge');
    const bell   = $('#notifBellBtn');
    const sidebarBadge = $('.sidebar-nav .nav-link [class*="badge"]');

    if (data.unread > 0) {
      // Update badge count
      if (badge.length) {
        badge.text(data.unread);
      } else {
        // Create badge if it doesn't exist
        bell.append(
          `<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill
            ${data.critical > 0 ? 'bg-danger blink' : 'bg-primary'}" id="notifBadge">
            ${data.unread}</span>`
        );
      }
      // Bell color
      bell.find('i').removeClass('text-secondary').addClass(data.critical > 0 ? 'text-danger' : 'text-primary');
      if (data.critical > 0) {
        bell.addClass('bell-ring');
      }
    } else {
      badge.remove();
      bell.find('i').removeClass('text-danger text-primary').addClass('text-secondary');
      bell.removeClass('bell-ring');
    }
  }

  function refreshNotifDropdown(data) {
    if (!data.recent || data.recent.length === 0) {
      $('#notifList').html(
        `<div class="text-center text-muted py-4">
          <i class="bi bi-check-circle fs-4"></i>
          <p class="mb-0 mt-1 small">Aucune notification</p>
        </div>`
      );
      return;
    }

    let html = '';
    data.recent.forEach(function (n) {
      const critClass = n.priority === 'critique' ? 'notif-critique' :
                        n.priority === 'important' ? 'notif-important' : 'notif-normal';
      const textClass = n.priority === 'critique' ? 'text-danger' :
                        n.priority === 'important' ? 'text-warning' : 'text-info';
      html += `
        <a href="/projets/${n.project_id}/"
           class="notif-item d-flex gap-2 px-3 py-2 text-decoration-none border-bottom ${critClass}">
          <div class="notif-icon mt-1">
            <i class="bi ${n.icon} ${textClass}"></i>
          </div>
          <div class="flex-grow-1 overflow-hidden">
            <div class="notif-msg small">${n.message}</div>
            <div class="notif-meta d-flex justify-content-between mt-1">
              <span class="text-muted" style="font-size:.72rem;">${n.project_name.substring(0, 25)}</span>
              <span class="text-muted" style="font-size:.72rem;">${n.created_at}</span>
            </div>
          </div>
        </a>`;
    });
    $('#notifList').html(html);
  }

  function pollNotifications() {
    $.getJSON('/notifications/api/')
      .done(function (data) {
        updateNotifBadge(data);
        refreshNotifDropdown(data);
      })
      .fail(function () {
        // Silent fail – don't disrupt UX
      });
  }

  // Poll every 60 seconds
  setInterval(pollNotifications, 60000);

  // ── Mark notification read on AJAX ──────────────
  $(document).on('click', '[data-notif-read]', function (e) {
    e.preventDefault();
    const pk  = $(this).data('notif-read');
    const btn = $(this);
    $.post(`/notifications/${pk}/lue/`, { csrfmiddlewaretoken: getCsrfToken() })
      .done(function () {
        btn.closest('.notif-row, .notif-item').addClass('opacity-50');
        pollNotifications();
      });
  });

  // ── CSRF helper ──────────────────────────────────
  function getCsrfToken() {
    return $('[name=csrfmiddlewaretoken]').val() ||
           document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
  }

});
