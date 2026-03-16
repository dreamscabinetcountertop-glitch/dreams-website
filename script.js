
document.addEventListener("DOMContentLoaded", function () {
  const estimateForm = document.getElementById("estimateForm");
  if (estimateForm) {
    estimateForm.addEventListener("submit", function(e){
      e.preventDefault();
      const v = id => document.getElementById(id)?.value || "";
      const subject = encodeURIComponent("New Estimate Request - " + (v("fullName") || "Website Lead"));
      const body = encodeURIComponent(
`New Estimate Request

Customer Information
Full Name: ${v("fullName")}
Phone: ${v("phone")}
Email: ${v("email")}
City / Location: ${v("city")}
Project Type: ${v("projectType")}
Project Timeline: ${v("timeline")}

Kitchen Measurements
Back Wall Length: ${v("backWall")}
Left Wall Length: ${v("leftWall")}
Right Wall Length: ${v("rightWall")}
Ceiling Height: ${v("ceilingHeight")}
Island Length: ${v("islandLength")}
Island Width: ${v("islandWidth")}

Window Measurements
Is There a Window?: ${v("hasWindow")}
Which Wall Is the Window On?: ${v("windowWall")}
Left Wall to Window: ${v("leftToWindow")}
Right Wall to Window: ${v("rightToWindow")}
Window Width: ${v("windowWidth")}
Window Height: ${v("windowHeight")}
Height From Floor to Window Bottom: ${v("windowSillHeight")}
Height From Floor to Window Top: ${v("windowTopHeight")}

Appliances / Layout
Sink Location: ${v("sinkLocation")}
Range / Stove Location: ${v("rangeLocation")}
Refrigerator Location: ${v("fridgeLocation")}
Microwave / Oven Location: ${v("microwaveLocation")}
Other Important Measurements: ${v("measurementsExtra")}

Design Preferences
Cabinet Color Preference: ${v("cabinetStyle")}
Countertop Preference: ${v("countertopStyle")}

Project Details
${v("details")}

Photo Upload Note
Please attach kitchen photos manually before sending.`
      );
      window.location.href = "mailto:dreamscabinetcountertop@gmail.com?subject=" + subject + "&body=" + body;
    });
  }

  const appointmentForm = document.getElementById("appointmentForm");
  if (appointmentForm) {
    appointmentForm.addEventListener("submit", function(e){
      e.preventDefault();
      const v = id => document.getElementById(id)?.value || "";
      const subject = encodeURIComponent("New Appointment Request - " + (v("apptName") || "Website Lead"));
      const body = encodeURIComponent(
`New Appointment Request

Full Name: ${v("apptName")}
Phone: ${v("apptPhone")}
Email: ${v("apptEmail")}
Product Interest: ${v("apptInterest")}
Preferred Date: ${v("apptDate")}
Preferred Time: ${v("apptTime")}

Notes
${v("apptNotes")}`
      );
      window.location.href = "mailto:dreamscabinetcountertop@gmail.com?subject=" + subject + "&body=" + body;
    });
  }
});
