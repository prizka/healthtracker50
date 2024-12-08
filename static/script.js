// First Document Ready: Calendar and Dashboard Charts
$(document).ready(function () {
  console.log("Main dashboard scripts loaded");

  // Helper Function: Get query parameter from URL
  const getQueryParam = (param) => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  };

  // Get current year
  const currentYear = new Date().getFullYear();

  // Handle month button clicks for redirection
  $('.month-btn').on('click', function () {
    const month = $(this).data('month');
    const year = $(this).data('year') || currentYear;
    console.log(`Redirecting to /dashboard for month: ${month}, year: ${year}`);
    window.location.href = `/dashboard?month=${month}&year=${year}`;
  });

  // Initialize calendar elements
  const daysTag = document.querySelector(".days");
  const currentDate = document.querySelector(".current-date");
  const prevNextIcon = document.querySelectorAll(".icons span");

  // Get the log date from URL if it exists
  const urlPath = window.location.pathname;
  const logDateMatch = urlPath.match(/\/log\/(\d{4}-\d{2}-\d{2})/);

  // Initialize date variables
  let date = new Date();
  let currYear, currMonth;
  if (logDateMatch) {
    // If we're on a log page, use the date from URL
    const logDate = new Date(logDateMatch[1]);
    currYear = logDate.getFullYear();
    currMonth = logDate.getMonth();
  } else {
    // Otherwise use URL parameters or current date
    currYear = parseInt(getQueryParam('year')) || date.getFullYear();
    currMonth = (parseInt(getQueryParam('month')) || (date.getMonth() + 1)) - 1;
  }

  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const renderCalendar = () => {
    let liTag = "";

    // Calculate first day of the month
    const firstDayOfMonth = new Date(currYear, currMonth, 1).getDay();
    // Calculate last date of the month
    const lastDateOfMonth = new Date(currYear, currMonth + 1, 0).getDate();
    // Calculate last day of the month
    const lastDayOfMonth = new Date(currYear, currMonth, lastDateOfMonth).getDay();
    // Calculate last date of previous month
    const lastDateOfLastMonth = new Date(currYear, currMonth, 0).getDate();

    // Add previous month's last days
    for (let i = firstDayOfMonth; i > 0; i--) {
      liTag += `<li class="inactive">${lastDateOfLastMonth - i + 1}</li>`;
    }

    // Add current month's days
    for (let i = 1; i <= lastDateOfMonth; i++) {
      const formattedDate = `${currYear}-${String(currMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;

      // Check for today
      const isToday = i === date.getDate() && currMonth === date.getMonth() && currYear === date.getFullYear();

      // Check for selected date from URL
      const isSelected = logDateMatch && logDateMatch[1] === formattedDate;

      // Determine class name
      let className = "";
      if (isToday) {
        className = "active";
      }
      if (isSelected) {
        className = className ? `${className} selected` : "selected";
      }

      liTag += `<li class="${className}" data-date="${formattedDate}">${i}</li>`;
    }

    // Add next month's first days
    for (let i = lastDayOfMonth; i < 6; i++) {
      liTag += `<li class="inactive">${i - lastDayOfMonth + 1}</li>`;
    }

    // Update the text for current month and year
    if (currentDate) {
      currentDate.innerText = `${months[currMonth]} ${currYear}`;
    }
    if (daysTag) {
      daysTag.innerHTML = liTag;

      // Add click event to active days
      const allDays = document.querySelectorAll(".days li:not(.inactive)");
      allDays.forEach((day) => {
        day.addEventListener("click", function () {
          const selectedDate = this.dataset.date;
          console.log(`Redirecting to /log/${selectedDate}`);
          window.location.href = `/log/${selectedDate}`;
        });
      });
    }
  };

  // Initialize separate charts for blood pressure and blood glucose
  let bloodPressureChart;
  let bloodGlucoseChart;

  async function initializeCharts() {
    // Initialize Blood Pressure Chart
    const bpCtx = document.getElementById("bloodPressureChart")?.getContext("2d");
    if (bpCtx) {
      bloodPressureChart = new Chart(bpCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [
            {
              label: "Systole",
              data: [],
              borderColor: "rgba(255, 99, 132, 1)",
              backgroundColor: "rgba(255, 99, 132, 0.2)",
              tension: 0.4,
            },
            {
              label: "Diastole",
              data: [],
              borderColor: "rgba(54, 162, 235, 1)",
              backgroundColor: "rgba(54, 162, 235, 0.2)",
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: "top",
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: "Date",
              },
            },
            y: {
              title: {
                display: true,
                text: "Blood Pressure (mmHg)",
              },
            },
          },
        },
      });
    }

    // Initialize Blood Glucose Chart
    const bgCtx = document.getElementById("bloodGlucoseChart")?.getContext("2d");
    if (bgCtx) {
      bloodGlucoseChart = new Chart(bgCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [
            {
              label: "Blood Glucose",
              data: [],
              borderColor: "rgba(75, 192, 192, 1)",
              backgroundColor: "rgba(75, 192, 192, 0.2)",
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: "top",
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: "Date",
              },
            },
            y: {
              title: {
                display: true,
                text: "Blood Glucose (mg/dL)",
              },
            },
          },
        },
      });
    }

    // Fetch initial data
    await fetchDashboardLogs(currMonth + 1, currYear);
  }

  // Function to fetch logs data and update both charts
  async function fetchDashboardLogs(month, year) {
    try {
      const response = await fetch(`/logs_chart?month=${month}&year=${year}`);
      const data = await response.json();

      if (bloodPressureChart) {
        bloodPressureChart.data.labels = data.dates;
        bloodPressureChart.data.datasets[0].data = data.systole;
        bloodPressureChart.data.datasets[1].data = data.diastole;
        bloodPressureChart.update();
      }

      if (bloodGlucoseChart) {
        bloodGlucoseChart.data.labels = data.dates;
        bloodGlucoseChart.data.datasets[0].data = data.sugar;
        bloodGlucoseChart.update();
      }
    } catch (error) {
      console.error("Error fetching dashboard logs:", error);
    }
  }

  // Initialize charts if we're on the dashboard page
  if (document.getElementById("bloodPressureChart") && document.getElementById("bloodGlucoseChart")) {
    initializeCharts();
  }

  // Initialize calendar if elements exist
  if (daysTag && currentDate) {
    renderCalendar();

    // Handle next/previous icons
    prevNextIcon.forEach(function (icon) {
      icon.addEventListener("click", function () {
        currMonth = this.id === "prev" ? currMonth - 1 : currMonth + 1;

        if (currMonth < 0) {
          currMonth = 11;
          currYear -= 1;
        }
        if (currMonth > 11) {
          currMonth = 0;
          currYear += 1;
        }

        const newMonth = currMonth + 1;
        console.log(`Redirecting to /dashboard for month: ${newMonth}, year: ${currYear}`);
        window.location.href = `/dashboard?month=${newMonth}&year=${currYear}`;
      });
    });
  }
});

// Second Document Ready: Lab Charts and Forms
$(document).ready(function () {
  console.log("Lab charts scripts loaded");

  let lipidChart;
  let hba1cChart;

  // Initialize Lipid Profile Chart
  function initializeLipidChart() {
    const ctx = document.getElementById("lipidChart")?.getContext("2d");
    if (!ctx) return;

    lipidChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "LDL",
            data: [],
            borderColor: "rgba(255, 99, 132, 1)",
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            tension: 0.4,
          },
          {
            label: "HDL",
            data: [],
            borderColor: "rgba(54, 162, 235, 1)",
            backgroundColor: "rgba(54, 162, 235, 0.2)",
            tension: 0.4,
          },
          {
            label: "Triglyceride",
            data: [],
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "top",
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Date",
            }
          },
          y: {
            title: {
              display: true,
              text: "Values (mg/dL)",
            },
          },
        },
      },
    });
  }

  // Initialize HbA1c Chart
  function initializeHba1cChart() {
    const ctx = document.getElementById("hba1cChart")?.getContext("2d");
    if (!ctx) return;

    hba1cChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: "HbA1c",
          data: [],
          borderColor: "rgba(153, 102, 255, 1)",
          backgroundColor: "rgba(153, 102, 255, 0.2)",
          tension: 0.4,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "top",
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Date",
            }
          },
          y: {
            title: {
              display: true,
              text: "HbA1c (%)",
            },
            suggestedMin: 4,
            suggestedMax: 14,
          },
        },
      },
    });
  }

  // Fetch and update lab data
  async function fetchLabData() {
    try {
        const response = await fetch('/lab_graph');
        const data = await response.json();

        // Update lipid chart
        if (lipidChart) {
            lipidChart.data.labels = data.lipid_dates.map(date => new Date(date).toLocaleDateString());
            lipidChart.data.datasets[0].data = data.ldl;
            lipidChart.data.datasets[1].data = data.hdl;
            lipidChart.data.datasets[2].data = data.triglyceride;
            lipidChart.update();
        }

        // Update HbA1c chart
        if (hba1cChart) {
            hba1cChart.data.labels = data.hba1c_dates.map(date => new Date(date).toLocaleDateString());
            hba1cChart.data.datasets[0].data = data.hba1c;
            hba1cChart.update();
        }
    } catch (error) {
        console.error("Error fetching lab data:", error);
    }
}

  // Initialize lab charts if we're on the lab report page
  if (document.getElementById("lipidChart") && document.getElementById("hba1cChart")) {
    console.log("Initializing lab charts");
    initializeLipidChart();
    initializeHba1cChart();
    fetchLabData();
  }

  // Handle lab form submissions only
  $(".lab-form form, form.lab-form").on("submit", async function(e) {
    e.preventDefault();
    const formData = new FormData(this);

    try {
      const response = await fetch('/save_lab', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        // Refresh the charts after successful submission
        fetchLabData();
        this.reset();
        alert("Lab data saved successfully!");
      } else {
        alert("Error saving data");
      }
    } catch (error) {
      console.error('Error:', error);
      alert("Error saving data");
    }
  });
});
