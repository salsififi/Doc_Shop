# DocShop
Exercice de création de back-end d'un site marchand proposé sur [Docstring.fr](www.docstring.fr).

## 2024-11-09: Problème actuel d'intégration de Stripe
Dans la vue [stripe_checkout_session](store/views.py), il y a un problème avec la ligne 84
`checkout_data["customer"] = user.stripe_id` qui déclenche une [erreur](problems/Erreur paramètre customer 2024-11-09 062703.png).
Si le bloc if/else contenant cette ligne est commenté, la page de paiement de Stripe s'affiche correctement.
Merci de votre aide!
