function access(i, j) {
    let $element = $('tr:nth-of-type(' + (i + 1) + ') td:nth-of-type(' + (j + 1) + ')');
    return $element;
}


$(document).ready(() => {
    $("#metismenu").metisMenu();
    let i = 0;
    for (i = 0; i < 6; i++) {
        console.log(i);
        let j = 0;
        for (j = 0; j < 6; j++) {
            let $td = access(i, j);
            let a = i;
            let b = j;
            $td.on('click', () => {
                $td.html('<i class="fa fa-check-circle" aria-hidden="true" style="color:blue"></i>');
                $.ajax({
                    url: 'http://127.0.0.1:8000/play/tickCell/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        a: a,
                        b: b
                    }
                }).done((result) => {

                    let response = JSON.parse(result);
                    console.log(response);
                    switch (response.status) {
                        case 1:
                            console.log('Win');
                            break;
                        case -1:
                            i = response.robotCell[0];
                            j = response.robotCell[1];
                            access(i, j).html('<i class="fa fa-check-circle" aria-hidden="true" style="color:red"></i>');
                            console.log('L');
                            break;
                        default:
                            i = response.robotCell[0];
                            j = response.robotCell[1];
                            access(i, j).html('<i class="fa fa-check-circle" aria-hidden="true" style="color:red"></i>');

                            break;
                    }

                })

            })
        }
    }
    console.log(i);
})