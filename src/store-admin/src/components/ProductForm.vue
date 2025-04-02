<template>
<div class="action-button">
    <button @click="saveProduct" class="button">Save Product</button>
</div>
<br />
<div v-if="showValidationErrors" class="error">
    <br />
    <ul v-for="error in validationErrors" :key="error">
        <li>{{ error }}</li>
    </ul>
</div>
<div class="product-form">
    <div class="form-row">
        <label for="product-name">Name</label>
        <input id="product-name" placeholder="Product Name" v-model="product.name" />
    </div>

    <div class="form-row">
        <label for="product-price">Price</label>
        <input id="product-price" placeholder="Product Price" v-model="product.price" type="number" step="0.01" />
    </div>

    <div class="form-row">
        <label for="product-tags">Keywords</label>
        <input id="product-tags" placeholder="Product Keywords" v-model="product.tags" />
    </div>

    <div class="form-row">
        <label for="product-description">Description</label>
        <textarea id="product-description" placeholder="Product Description" v-model="product.description" />
        <button @click="generateDescription" class="ai-button">Ask OpenAI</button>
      <input type="hidden" id="product-id" placeholder="Product ID" v-model="product.id" />
    </div>

    <v-file-input show-size v-model="img" @change="upload(img)" label="Image"></v-file-input>

    <div class="product-image">
      <img :src="product.image" alt="Product Image" id="prod-image"/>
    </div>

    <div class="form-row">
      <label for="product-image">Image</label>
      <input id="product-image" placeholder="Product Image" v-model="product.image" />
    </div>
  </div>
</template>

<script>
const aiServiceUrl = '/ai/';
const productServiceUrl = '/product/';

export default {
    name: 'ProductForm',
    props: ['products'],
    emits: ['addProductsToList', 'updateProductInList'],
    data() {
        return {
            product: {
                id: 0,
                name: '',
                image: '/placeholder.png',
                description: '',
                price: 0.00,
                tags: []
            },
            showValidationErrors: false
        }
    },
    mounted() {
        // if we're editing a product, get the product details
        if (this.$route.params.id) {
            // get the product from the products list
            const product = this.products.find(product => product.id == this.$route.params.id)
            // copy the product details into the product object
            this.product = Object.assign({}, product);
            // add empty tags if the product doesn't have any
            if (!this.product.tags) {
                this.product.tags = [];
            }
        }

        // if the AI service is not responding, hide the button
        fetch(`${aiServiceUrl}health`)
            .then(response => {
                if (response.ok) {
                    console.log('AI service is healthy');
                } else {
                    console.log('AI service is not healthy');
                    document.getElementsByClassName('ai-button')[0].style.display = 'none';
                }
            })
            .catch(error => {
                console.log('Error calling the AI service');
                console.log(error)
                document.getElementsByClassName('ai-button')[0].style.display = 'none';
            })
    },
    computed: {
        validationErrors() {
            let errors = [];
            if (this.product.name.length === 0) {
                errors.push('Please enter a value for the name field');
            }

            if (this.product.description.length === 0) {
                errors.push('Please enter a value for the description field');
            }

            if (this.product.price <= 0) {
                errors.push('Please enter a value greater than 0 for the price field');
            }

            return errors;
        }
    },
    methods: {
        generateDescription() {
            // Ensure the tag has a value
            if (this.product.tags.length === 0) {
                alert('Please enter a value for the keywords field before asking AI service');
                return;
            }

            const intervalId = this.waitForAI();

            // Prepare the request body
            let requestBody = {
                name: this.product.name,
                tags: this.product.tags.split(',').map(tag => tag.trim()),
                image: this.product.image // Include the product image
            };

            console.log("<< Sending request body >>", requestBody);
            this.product.description = "";

            // If the image is a file, convert it to base64
            // and send it to the AI service
            // Otherwise, send the existing product.image

            //const imageInput = this.$refs.productImage;
            const image = document.getElementById('prod-image');
            alert('Image source: ' + image.src);

            // Get the remote image as a Blob with the fetch API
            fetch(image.src)
                .then(response => response.blob())
                .then(blob => {
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            requestBody["image"] = reader.result; // Set the base64-encoded image
                            alert('Image uploaded successfully. Generating product description... ');
                            console.log("<< Sending request body with image >>", requestBody);
                            // Send the request with the updated requestBody
                            fetch(`${aiServiceUrl}generate/description`, {
                                    method: 'POST',
                                    body: JSON.stringify(requestBody)
                                })
                                .then(response => response.json())
                                .then(product => {
                                    this.product.description = product.description;
                                })
                                .catch(error => {
                                    console.log(error);
                                    alert('Error occurred while generating product description');
                                })
                                .finally(() => {
                                    clearInterval(intervalId);
                                });
                        };
                        reader.readAsDataURL(blob); // Convert the blob to base64
                        })
                        .catch(error => {
                            console.log(error);
                            alert('Error occurred while generating product description');
                        })
                        .finally(() => {
                            clearInterval(intervalId);
                        });
                    },
                    waitForAI() {
                        let dots = '';
                        const intervalId = setInterval(() => {
                            dots += '.';
                            this.product.description = `Thinking${dots}`;
                        }, 500);
                        return intervalId;
                    },
                    saveProduct() {
                        if (this.validationErrors.length > 0) {
                            this.showValidationErrors = true;
                            return;
                        }

                        // default to updates
                        let method = 'PUT';

                        // get the path of the current request
                        let path = this.$route.path;
                        if (path.includes('add')) {
                            method = 'POST';
                        }

                        // ensure product.price is not wrapped in quotes
                        this.product.price = parseFloat(this.product.price);

                        // upsert the product
                        fetch(`${productServiceUrl}`, {
                                method: method,
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(this.product)
                            })
                            .then(response => response.json())
                            .then(product => {
                                alert('Product saved successfully')
                                // update or add the product to the list
                                if (method === 'PUT') {
                                    this.$emit('updateProductInList', this.product);
                                } else {
                                    this.$emit('addProductsToList', product);
                                }
                                // route to product detail
                                this.$router.push(`/product/${product.id}`);
                            })
                            .catch(error => {
                                console.log(error)
                                alert('Error occurred while saving product')
                            })
                    }
                }
        }
</script>

<style scoped>
ul {
    justify-content: center;
    list-style: none;
    margin: 0;
    padding: 0;
    width: 100%;
    color: #ff0000;
}

.product-image {
    text-align: center;
    margin: 10px 0;
}

.product-image img {
    max-width: 100%;
    height: auto;
    border: 1px solid #ccc;
    border-radius: 5px;
}
</style>
