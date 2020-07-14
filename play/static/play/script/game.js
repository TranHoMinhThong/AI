var _turn = 0;

function access(i, j) {
  let $element = $(
    "tr:nth-of-type(" + (i + 1) + ") td:nth-of-type(" + (j + 1) + ")"
  );
  return $element;
}

var turnName = document.getElementById("name");

$(document).ready(() => {
  $("#metismenu").metisMenu();
  $("#btn-start").on("click", function () {
    if ($("#btn-start").text() == "Start") {
      $("#btn-start").html("Restart");
    } else {
      _turn = 0;
      $.ajax({
        url: "http://127.0.0.1:8000/play/tickCell/",
        type: "POST",
        dataType: "json",
        data: {
          a: -1,
          b: -1,
        },
      }).done(() => {
        let i = 0;
        for (i = 0; i < 6; i++) {
          let j = 0;
          for (j = 0; j < 6; j++) {
            let $td = access(i, j);
            let a = i;
            let b = j;
            $td.html("");
          }
        }
        $("#result").html("");
      });
    }
    let i = 0;
    for (i = 0; i < 6; i++) {
      let j = 0;
      for (j = 0; j < 6; j++) {
        let $td = access(i, j);
        let a = i;
        let b = j;
        $td.on("click", () => {
          if (_turn % 2 == 0 && !$td.html()) {
            $td.html(
              '<i class="far fa-circle fa-3x" aria-hidden="true" style="color:blue"></i>'
            );
            _turn++;
            turnName.innerHTML = "Computer";
            turnName.style.color = "red";
            $.ajax({
              url: "http://127.0.0.1:8000/play/tickCell/",
              type: "POST",
              dataType: "json",
              data: {
                a: a,
                b: b,
              },
            }).done((result) => {
              let response = JSON.parse(result);
              turnName.innerHTML = "Player";
              turnName.style.color = "blue";
              if (response.node) {
                let cell = response.node.children[0].cell;
                $("#s-row").html(`Hàng ${cell[0] + 1} `);
                $("#s-col").html(`Cột ${cell[1] + 1}`);
              } else {
                $("#s-row").html(``);
                $("#s-col").html(``);
              }
              switch (response.status) {
                case 1:
                  console.log("Win");
                  $("#result").html("Congration. You Win!");
                  $("#result").css("color", "blue");
                  break;
                case -1:
                  i = response.robotCell[0];
                  j = response.robotCell[1];
                  access(i, j).html(
                    '<i class="fas fa-times fa-4x" style="color:red;" ></i>'
                  );
                  console.log("L");
                  $("#result").html("You Lose. Try again!");
                  $("#result").css("color", "red");
                  break;
                default:
                  i = response.robotCell[0];
                  j = response.robotCell[1];
                  access(i, j).html(
                    '<i class="fas fa-times fa-4x" style="color:red"></i>'
                  );
                  _turn++;
                  break;
              }
            });
          }
        });
      }
    }
  });
});
