import { Routes } from '@angular/router';
import { LandingPage } from './landing-page/landing-page';
import { Register } from './register/register';
import { Login } from './login/login';
import { MyProfile } from './my-profile/my-profile';
import { Stores } from './stores/stores';
import { Products } from './products/products';
import { ProductDetailComponent } from './products/product-detail/product-detail';

export const routes: Routes = [
    { path: '', component: LandingPage },
    { path: 'register', component: Register },
    { path: 'login', component: Login },
    { path: 'my-profile', component: MyProfile },
    { path: 'stores', component: Stores },
    { path: 'products', component: Products },
    { path: 'products/:id', component: ProductDetailComponent }
];
