function delete_food_item(id) {
    fetch("/food_item/" + parseInt(id), {
        method: "DELETE",
    }).then(function (response) {
        if (response.ok) {
            window.location.reload();
        }
    });
}

function edit_food_item(id, new_quantity) {
    new_quantity = parseInt(new_quantity);
    fetch("/food_item/" + id + "/" + new_quantity, {
        method: "PUT",
    }).then(function (response) {
        if (response.ok) {
            window.location.reload();
        }
    });
}

function plus_one(id, current_quantity) {
    current_quantity = parseInt(current_quantity);
    edit_food_item(id, current_quantity + 1);
}

function minus_one(id, current_quantity) {
    current_quantity = parseInt(current_quantity);
    if (current_quantity - 1 <= 0) {
        delete_food_item(id);
    } else {
        edit_food_item(id, current_quantity - 1);
    }
}

function add_food_item(name, quantity) {
    fetch("/food_item", {
        method: "POST",
        body: JSON.stringify({
            name: name,
            quantity: parseInt(quantity),
        }),
        headers: {
            "Content-Type": "application/json",
        },
    }).then(function (response) {
        if (response.ok) {
            window.location.reload();
        }
    });
}

document.getElementById("btn_add").addEventListener("click", function () {
    let name = document.getElementById("name_add").value;
    let quantity = document.getElementById("quantity_add").value;
    
    add_food_item(name, quantity);
});